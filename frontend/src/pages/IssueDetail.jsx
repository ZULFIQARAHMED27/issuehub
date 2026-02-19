import { useCallback, useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import api from "../api/axios";
import StatusBadge from "../components/StatusBadge";
import Toast from "../components/Toast";

export default function IssueDetail() {
  const { projectId, issueId } = useParams();
  const navigate = useNavigate();

  const [issue, setIssue] = useState(null);
  const [comments, setComments] = useState([]);
  const [members, setMembers] = useState([]);
  const [newComment, setNewComment] = useState("");
  const [currentUser, setCurrentUser] = useState(null);
  const [toast, setToast] = useState(null);
  const [submittingComment, setSubmittingComment] = useState(false);
  const [savingMeta, setSavingMeta] = useState(false);
  const [initialLoadFailed, setInitialLoadFailed] = useState(false);
  const [editForm, setEditForm] = useState({
    title: "",
    description: "",
    priority: "medium"
  });

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

  const fetchIssue = useCallback(async () => {
    try {
      const res = await api.get(`/issues/${issueId}`);
      setIssue(res.data);
      setEditForm({
        title: res.data.title || "",
        description: res.data.description || "",
        priority: res.data.priority || "medium"
      });
      setInitialLoadFailed(false);
    } catch (err) {
      setInitialLoadFailed(true);
      handleApiError(err, "Failed to load issue");
    }
  }, [handleApiError, issueId]);

  const fetchComments = useCallback(async () => {
    try {
      const res = await api.get(`/issues/${issueId}/comments`);
      setComments(res.data);
    } catch (err) {
      handleApiError(err, "Failed to load comments");
    }
  }, [handleApiError, issueId]);

  const fetchMembers = useCallback(async () => {
    try {
      const res = await api.get(`/projects/${projectId}/members`);
      setMembers(res.data);
    } catch (err) {
      handleApiError(err, "Failed to load members");
    }
  }, [handleApiError, projectId]);

  const fetchMe = useCallback(async () => {
    try {
      const res = await api.get("/me");
      setCurrentUser(res.data);
    } catch (err) {
      handleApiError(err, "Failed to load current user");
    }
  }, [handleApiError]);

  useEffect(() => {
    fetchIssue();
    fetchComments();
    fetchMembers();
    fetchMe();
  }, [fetchComments, fetchIssue, fetchMe, fetchMembers]);

  const normalizeRole = (role) => {
    if (!role) return "";
    return String(role).split(".").pop();
  };

  const isMaintainer = normalizeRole(
    members.find((m) => m.id === currentUser?.id)?.role
  ) === "maintainer";
  const isReporter = issue?.reporter_id === currentUser?.id;
  const canEditOwnFields = isMaintainer || isReporter;

  const handleStatusChange = async (status) => {
    if (!isMaintainer) {
      showToast("Only maintainers can change status", "error");
      return;
    }

    try {
      await api.patch(`/issues/${issueId}`, { status });
      fetchIssue();
      showToast("Status updated", "success");
    } catch (err) {
      showToast(
        err.response?.data?.error?.message || "Failed to update status",
        "error"
      );
    }
  };

  const handleAssignChange = async (assignee_id) => {
    if (!isMaintainer) {
      showToast("Only maintainers can assign issues", "error");
      return;
    }

    try {
      await api.patch(`/issues/${issueId}`, {
        assignee_id: assignee_id || null
      });
      fetchIssue();
      showToast("Assignee updated", "success");
    } catch (err) {
      showToast(
        err.response?.data?.error?.message || "Failed to update assignee",
        "error"
      );
    }
  };

  const handleAddComment = async () => {
    if (!newComment.trim()) return;

    try {
      setSubmittingComment(true);
      await api.post(`/issues/${issueId}/comments`, {
        body: newComment
      });

      setNewComment("");
      fetchComments();
      showToast("Comment added", "success");
    } catch (err) {
      showToast(
        err.response?.data?.error?.message || "Failed to add comment",
        "error"
      );
    } finally {
      setSubmittingComment(false);
    }
  };

  const handleMetaUpdate = async (e) => {
    e.preventDefault();
    if (!canEditOwnFields) {
      showToast("Not allowed to update this issue", "error");
      return;
    }

    try {
      setSavingMeta(true);
      await api.patch(`/issues/${issueId}`, {
        title: editForm.title,
        description: editForm.description,
        priority: editForm.priority
      });
      await fetchIssue();
      showToast("Issue updated", "success");
    } catch (err) {
      showToast(
        err.response?.data?.error?.message || "Failed to update issue",
        "error"
      );
    } finally {
      setSavingMeta(false);
    }
  };

  if (!issue) {
    if (initialLoadFailed) {
      return <p>Unable to load issue right now. Please try again.</p>;
    }
    return (
      <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
        <span className="spinner" />
        <p>Loading issue...</p>
      </div>
    );
  }

  const getUserName = (id) => {
    const user = members.find((m) => m.id === id);
    return user ? user.name : `User #${id}`;
  };

  return (
    <div className="container">
      <button
        className="secondary-btn"
        onClick={() => navigate(`/projects/${projectId}`)}
      >
        ← Back to Project
      </button>

      <div className="card" style={{ marginTop: "20px" }}>
        {canEditOwnFields ? (
          <form onSubmit={handleMetaUpdate}>
            <input
              value={editForm.title}
              onChange={(e) =>
                setEditForm((prev) => ({ ...prev, title: e.target.value }))
              }
              required
              style={{ width: "100%", marginBottom: "10px" }}
            />
            <textarea
              rows="3"
              value={editForm.description}
              onChange={(e) =>
                setEditForm((prev) => ({
                  ...prev,
                  description: e.target.value
                }))
              }
              style={{ width: "100%", marginBottom: "10px", padding: "8px" }}
            />
            <div style={{ display: "flex", gap: "8px", alignItems: "center" }}>
              <select
                value={editForm.priority}
                onChange={(e) =>
                  setEditForm((prev) => ({
                    ...prev,
                    priority: e.target.value
                  }))
                }
              >
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
                <option value="critical">Critical</option>
              </select>

              <button type="submit" disabled={savingMeta}>
                {savingMeta ? "Saving..." : "Save Issue"}
              </button>
            </div>
          </form>
        ) : (
          <>
            <h2>{issue.title}</h2>
            <p>{issue.description}</p>
          </>
        )}

        <div style={{ marginTop: "20px" }}>
          <strong>Status:</strong>{" "}
          <StatusBadge status={issue.status} />

          {isMaintainer && (
            <select
              value={issue.status}
              onChange={(e) => handleStatusChange(e.target.value)}
              style={{ marginLeft: "10px" }}
            >
              <option value="open">Open</option>
              <option value="in_progress">In Progress</option>
              <option value="resolved">Resolved</option>
              <option value="closed">Closed</option>
            </select>
          )}
        </div>

        <div style={{ marginTop: "15px" }}>
          <strong>Priority:</strong> {issue.priority}
        </div>

        <div style={{ marginTop: "15px" }}>
          <strong>Reporter:</strong>{" "}
          {getUserName(issue.reporter_id)}
        </div>

        <div style={{ marginTop: "15px" }}>
          <strong>Assignee:</strong>

          {isMaintainer ? (
            <select
              value={issue.assignee_id || ""}
              onChange={(e) =>
                handleAssignChange(
                  e.target.value ? Number(e.target.value) : null
                )
              }
              style={{ marginLeft: "10px" }}
            >
              <option value="">Unassigned</option>
              {members.map((member) => (
                <option key={member.id} value={member.id}>
                  {member.name}
                </option>
              ))}
            </select>
          ) : (
            <span style={{ marginLeft: "10px" }}>
              {issue.assignee_name || "Unassigned"}
            </span>
          )}
        </div>

        <div style={{ marginTop: "15px" }}>
          <strong>Created:</strong>{" "}
          {issue.created_at ? new Date(issue.created_at).toLocaleString() : "-"}
        </div>

        <div style={{ marginTop: "15px" }}>
          <strong>Updated:</strong>{" "}
          {issue.updated_at ? new Date(issue.updated_at).toLocaleString() : "-"}
        </div>
      </div>

      <div className="card" style={{ marginTop: "20px" }}>
        <h3>Comments</h3>

        {comments.length === 0 ? (
          <p>No comments yet.</p>
        ) : (
          comments.map((comment) => (
            <div
              key={comment.id}
              style={{
                padding: "10px",
                borderBottom: "1px solid #eee"
              }}
            >
              {comment.body}
            </div>
          ))
        )}

        <div style={{ marginTop: "15px" }}>
          <textarea
            rows="3"
            placeholder="Add a comment..."
            value={newComment}
            onChange={(e) => setNewComment(e.target.value)}
            style={{ width: "100%", padding: "8px" }}
          />

          <button
            style={{ marginTop: "8px" }}
            disabled={submittingComment}
            onClick={handleAddComment}
          >
            {submittingComment ? "Adding..." : "Add Comment"}
          </button>
        </div>
      </div>

      <Toast
        message={toast?.message}
        type={toast?.type}
        onClose={() => setToast(null)}
      />
    </div>
  );
}
