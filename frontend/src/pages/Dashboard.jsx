import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api/axios";
import Toast from "../components/Toast";

export default function Dashboard() {
  const navigate = useNavigate();

  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [toast, setToast] = useState(null);
  const [currentUser, setCurrentUser] = useState(null);
  const [form, setForm] = useState({
    name: "",
    key: "",
    description: ""
  });

  useEffect(() => {
    fetchProjects();
  }, []);

  const showToast = (message, type = "success") => {
    setToast({ message, type });
    setTimeout(() => setToast(null), 3000);
  };

  const fetchProjects = async () => {
    try {
      setLoading(true);
      const [projectsRes, meRes] = await Promise.all([
        api.get("/projects"),
        api.get("/auth/me")
      ]);
      setProjects(projectsRes.data);
      setCurrentUser(meRes.data);
    } catch {
      showToast("Failed to load projects", "error");
    } finally {
      setLoading(false);
    }
  };

  const handleCreateProject = async (e) => {
    e.preventDefault();
    try {
      setSubmitting(true);
      await api.post("/projects", form);
      setForm({ name: "", key: "", description: "" });
      fetchProjects();
      showToast("Project created", "success");
    } catch (err) {
      showToast(
        err.response?.data?.error?.message || "Failed to create project",
        "error"
      );
    } finally {
      setSubmitting(false);
    }
  };

  const handleDeleteProject = async (projectId) => {
    const confirmDelete = window.confirm(
      "Are you sure you want to delete this project? This cannot be undone."
    );

    if (!confirmDelete) return;

    try {
      await api.delete(`/projects/${projectId}`);
      fetchProjects();
      showToast("Project deleted", "success");
    } catch {
      showToast("Failed to delete project", "error");
    }
  };

  const logout = () => {
    localStorage.removeItem("token");
    navigate("/login");
  };

  return (
    <div className="container">

      <div style={{ display: "flex", justifyContent: "space-between" }}>
        <h2>Dashboard</h2>
        <div style={{ display: "flex", gap: "8px", alignItems: "center" }}>
          <button type="button" className="secondary-btn" disabled>
            Logged in as {currentUser?.name || currentUser?.email || "User"}
          </button>
          <button className="secondary-btn" onClick={logout}>
            Logout
          </button>
        </div>
      </div>

      <div className="card" style={{ marginTop: "20px" }}>
        <h3>Create Project</h3>

        <form
          onSubmit={handleCreateProject}
          style={{ display: "flex", gap: "10px", flexWrap: "wrap" }}
        >
          <input
            placeholder="Project Name"
            value={form.name}
            onChange={(e) =>
              setForm({ ...form, name: e.target.value })
            }
            required
          />

          <input
            placeholder="Project Key"
            value={form.key}
            onChange={(e) =>
              setForm({ ...form, key: e.target.value })
            }
            required
          />

          <input
            placeholder="Description"
            value={form.description}
            onChange={(e) =>
              setForm({ ...form, description: e.target.value })
            }
          />

          <button type="submit" disabled={submitting}>
            {submitting ? "Creating..." : "Create"}
          </button>
        </form>
      </div>

      <div className="card" style={{ marginTop: "20px" }}>
        <h3>Your Projects</h3>

        {loading ? (
          <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
            <span className="spinner" />
            <p>Loading...</p>
          </div>
        ) : projects.length === 0 ? (
          <div style={{ textAlign: "center", padding: "20px", color: "#777" }}>
            📂 No projects yet. Create your first one.
          </div>
        ) : (
          projects.map((project) => (
            <div
              key={project.id}
              style={{
                padding: "15px",
                borderBottom: "1px solid #eee",
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center"
              }}
            >
              <div
                style={{ cursor: "pointer" }}
                onClick={() => navigate(`/projects/${project.id}`)}
              >
                <strong>{project.name}</strong> ({project.key})
                {project.description && (
                  <div style={{ fontSize: "13px", color: "#666" }}>
                    {project.description}
                  </div>
                )}
              </div>

              {project.my_role === "maintainer" && (
                <button
                  className="secondary-btn"
                  onClick={() => handleDeleteProject(project.id)}
                >
                  Delete
                </button>
              )}
            </div>
          ))
        )}
      </div>

      <Toast
        message={toast?.message}
        type={toast?.type}
        onClose={() => setToast(null)}
      />
    </div>
  );
}
