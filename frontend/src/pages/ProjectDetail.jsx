import { useCallback, useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import api from "../api/axios";
import IssueTable from "../components/IssueTable";
import Toast from "../components/Toast";

export default function ProjectDetail() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [project, setProject] = useState(null);
  const [issues, setIssues] = useState([]);
  const [members, setMembers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [submittingInvite, setSubmittingInvite] = useState(false);
  const [submittingIssue, setSubmittingIssue] = useState(false);
  const [showCreateIssueModal, setShowCreateIssueModal] = useState(false);
  const [toast, setToast] = useState(null);
  const [filters, setFilters] = useState({
    status: "",
    priority: "",
    assignee: "",
    q: "",
    sort: ""
  });

  // Pagination
  const [page, setPage] = useState(1);
  const [pageSize] = useState(5);
  const [total, setTotal] = useState(0);
  const totalPages = Math.ceil(total / pageSize);

  // Invite Member
  const [invite, setInvite] = useState({
    email: "",
    role: "member"
  });

  // Create Issue Form
  const [form, setForm] = useState({
    title: "",
    description: "",
    priority: "medium",
    assignee_id: ""
  });
  const normalizeRole = (role) => {
    if (!role) return "";
    return String(role).split(".").pop();
  };
  const isMaintainer = normalizeRole(project?.my_role) === "maintainer";

  const showToast = useCallback((message, type = "success") => {
    setToast({ message, type });
    setTimeout(() => setToast(null), 3000);
  }, []);

  const handleApiError = useCallback((err, fallbackMessage) => {
    if (err.response?.status === 401) {
      localStorage.removeItem("token");
      navigate("/login");
      return;
    }
    showToast(err.response?.data?.error?.message || fallbackMessage, "error");
  }, [navigate, showToast]);

  const fetchProject = useCallback(async () => {
    try {
      const res = await api.get("/projects");
      const found = res.data.find((p) => p.id === parseInt(id));
      setProject(found || null);
    } catch (err) {
      handleApiError(err, "Failed to load project");
    }
  }, [handleApiError, id]);

  const fetchMembers = useCallback(async () => {
    try {
      const res = await api.get(`/projects/${id}/members`);
      setMembers(res.data);
    } catch (err) {
      handleApiError(err, "Failed to load members");
    }
  }, [handleApiError, id]);

  const fetchIssues = useCallback(async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams({
        page: String(page),
        page_size: String(pageSize)
      });

      if (filters.status) params.set("status", filters.status);
      if (filters.priority) params.set("priority", filters.priority);
      if (filters.assignee) params.set("assignee", filters.assignee);
      if (filters.q.trim()) params.set("q", filters.q.trim());
      if (filters.sort) params.set("sort", filters.sort);

      const res = await api.get(`/projects/${id}/issues?${params.toString()}`);
      setIssues(res.data.data);
      setTotal(res.data.total);
    } catch (err) {
      handleApiError(err, "Failed to load issues");
    } finally {
      setLoading(false);
    }
  }, [filters, handleApiError, id, page, pageSize]);

  useEffect(() => {
    fetchProject();
    fetchMembers();
  }, [fetchMembers, fetchProject]);

  useEffect(() => {
    fetchIssues();
  }, [fetchIssues]);

  const handleFilterChange = (name, value) => {
    setPage(1);
    setFilters((prev) => ({ ...prev, [name]: value }));
  };

  const clearFilters = () => {
    setPage(1);
    setFilters({
      status: "",
      priority: "",
      assignee: "",
      q: "",
      sort: ""
    });
  };

  const handleInvite = async (e) => {
    e.preventDefault();
    try {
      setSubmittingInvite(true);
      await api.post(`/projects/${id}/members`, invite);
      setInvite({ email: "", role: "member" });
      fetchMembers();
      showToast("Member invited successfully", "success");
    } catch (err) {
      showToast(err.response?.data?.error?.message || "Invite failed", "error");
    } finally {
      setSubmittingInvite(false);
    }
  };

  const handleCreateIssue = async (e) => {
    e.preventDefault();
    try {
      setSubmittingIssue(true);
      await api.post(`/projects/${id}/issues`, {
        ...form,
        assignee_id: form.assignee_id || null
      });

      setForm({
        title: "",
        description: "",
        priority: "medium",
        assignee_id: ""
      });

      setPage(1);
      fetchIssues();
      setShowCreateIssueModal(false);
      showToast("Issue created", "success");
    } catch {
      showToast("Failed to create issue", "error");
    } finally {
      setSubmittingIssue(false);
    }
  };

  const handleStatusChange = async (issueId, status) => {
    if (!isMaintainer) {
      showToast("Only maintainers can change status", "error");
      return;
    }

    try {
      await api.patch(`/issues/${issueId}`, { status });
      setIssues((prev) =>
        prev.map((issue) =>
          issue.id === issueId ? { ...issue, status } : issue
        )
      );
    } catch (err) {
      showToast(
        err.response?.data?.error?.message || "Failed to update status",
        "error"
      );
    }
  };

  const handleAssignChange = async (issueId, assigneeId) => {
    if (!isMaintainer) {
      showToast("Only maintainers can assign issues", "error");
      return;
    }

    try {
      await api.patch(`/issues/${issueId}`, {
        assignee_id: assigneeId ?? null
      });
      setIssues((prev) =>
        prev.map((issue) =>
          issue.id === issueId
            ? { ...issue, assignee_id: assigneeId ?? null }
            : issue
        )
      );
    } catch (err) {
      showToast(
        err.response?.data?.error?.message || "Failed to update assignee",
        "error"
      );
    }
  };

  const handleDeleteIssue = async (issueId) => {
    const ok = window.confirm("Delete this issue?");
    if (!ok) return;

    try {
      await api.delete(`/issues/${issueId}`);
      fetchIssues();
      showToast("Issue deleted", "success");
    } catch (err) {
      showToast(
        err.response?.data?.error?.message || "Failed to delete issue",
        "error"
      );
    }
  };

  return (
    <div className="container">

      {/* Project Header */}
      <div className="card">
        <div style={{ display: "flex", justifyContent: "space-between" }}>
          <div>
            <h2>
              {project
                ? `${project.name} (${project.key})`
                : "Loading project..."}
            </h2>

            {project?.description && (
              <p style={{ marginTop: "5px", color: "#666" }}>
                {project.description}
              </p>
            )}
          </div>

          <button
            className="secondary-btn"
            onClick={() => navigate("/dashboard")}
          >
            Back
          </button>
        </div>
      </div>

      {/* Invite Member */}
      {isMaintainer && (
        <div className="card">
          <h3>Invite Member</h3>

          <form
            onSubmit={handleInvite}
            style={{ display: "flex", gap: "10px", flexWrap: "wrap" }}
          >
            <input
              type="email"
              placeholder="User Email"
              value={invite.email}
              onChange={(e) =>
                setInvite({ ...invite, email: e.target.value })
              }
              required
            />

            <select
              value={invite.role}
              onChange={(e) =>
                setInvite({ ...invite, role: e.target.value })
              }
            >
              <option value="member">Member</option>
              <option value="maintainer">Maintainer</option>
            </select>

            <button type="submit" disabled={submittingInvite}>
              {submittingInvite ? "Inviting..." : "Invite"}
            </button>
          </form>

          <div style={{ marginTop: "15px", fontSize: "14px" }}>
            <strong>Current Members:</strong>
            <ul>
              {members.map((m) => (
                <li key={m.id}>
                  {m.name} ({normalizeRole(m.role)})
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}

      {/* Issues Table */}
      <div className="card">
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <h3>Issues</h3>
          <button onClick={() => setShowCreateIssueModal(true)}>New Issue</button>
        </div>

        <div
          style={{
            display: "flex",
            gap: "10px",
            flexWrap: "wrap",
            marginBottom: "12px"
          }}
        >
          <input
            placeholder="Search title..."
            value={filters.q}
            onChange={(e) => handleFilterChange("q", e.target.value)}
          />

          <select
            value={filters.status}
            onChange={(e) => handleFilterChange("status", e.target.value)}
          >
            <option value="">All Statuses</option>
            <option value="open">Open</option>
            <option value="in_progress">In Progress</option>
            <option value="resolved">Resolved</option>
            <option value="closed">Closed</option>
          </select>

          <select
            value={filters.priority}
            onChange={(e) => handleFilterChange("priority", e.target.value)}
          >
            <option value="">All Priorities</option>
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
            <option value="critical">Critical</option>
          </select>

          <select
            value={filters.assignee}
            onChange={(e) => handleFilterChange("assignee", e.target.value)}
          >
            <option value="">All Assignees</option>
            {members.map((member) => (
              <option key={member.id} value={member.id}>
                {member.name}
              </option>
            ))}
          </select>

          <select
            value={filters.sort}
            onChange={(e) => handleFilterChange("sort", e.target.value)}
          >
            <option value="">Sort: Default</option>
            <option value="created_at">Created At</option>
            <option value="priority">Priority</option>
            <option value="status">Status</option>
          </select>

          <button className="secondary-btn" onClick={clearFilters}>
            Clear
          </button>
        </div>

        {loading ? (
          <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
            <span className="spinner" />
            <p>Loading...</p>
          </div>
        ) : (
          <IssueTable
            issues={issues}
            members={members}
            projectKey={project?.key}
            canManageAssignee={isMaintainer}
            canManageAllStatuses={isMaintainer}
            onStatusChange={handleStatusChange}
            onAssignChange={handleAssignChange}
            onDelete={handleDeleteIssue}
          />
        )}

        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            marginTop: "12px"
          }}
        >
          <button
            className="secondary-btn"
            onClick={() => setPage((p) => Math.max(1, p - 1))}
            disabled={page <= 1}
          >
            Previous
          </button>

          <span>
            Page {page} of {Math.max(1, totalPages)}
          </span>

          <button
            className="secondary-btn"
            onClick={() => setPage((p) => Math.min(totalPages || 1, p + 1))}
            disabled={page >= totalPages}
          >
            Next
          </button>
        </div>
      </div>

      <Toast
        message={toast?.message}
        type={toast?.type}
        onClose={() => setToast(null)}
      />

      {showCreateIssueModal && (
        <div className="modal-backdrop" onClick={() => setShowCreateIssueModal(false)}>
          <div className="modal-card" onClick={(e) => e.stopPropagation()}>
            <h3>Create Issue</h3>
            <form
              onSubmit={handleCreateIssue}
              style={{ display: "flex", flexDirection: "column", gap: "10px" }}
            >
              <input
                placeholder="Issue title"
                value={form.title}
                onChange={(e) =>
                  setForm({ ...form, title: e.target.value })
                }
                required
              />

              <textarea
                rows="3"
                placeholder="Description"
                value={form.description}
                onChange={(e) =>
                  setForm({ ...form, description: e.target.value })
                }
                style={{ width: "100%", padding: "8px" }}
              />

              <select
                value={form.priority}
                onChange={(e) =>
                  setForm({ ...form, priority: e.target.value })
                }
              >
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
                <option value="critical">Critical</option>
              </select>

              <select
                value={form.assignee_id}
                onChange={(e) =>
                  setForm({ ...form, assignee_id: e.target.value })
                }
              >
                <option value="">Unassigned</option>
                {members.map((member) => (
                  <option key={member.id} value={member.id}>
                    {member.name}
                  </option>
                ))}
              </select>

              <div style={{ display: "flex", gap: "8px", justifyContent: "flex-end" }}>
                <button
                  type="button"
                  className="secondary-btn"
                  onClick={() => setShowCreateIssueModal(false)}
                >
                  Cancel
                </button>
                <button type="submit" disabled={submittingIssue}>
                  {submittingIssue ? "Creating..." : "Create Issue"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

    </div>
  );
}
