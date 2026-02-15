import { useNavigate, useParams } from "react-router-dom";
import StatusBadge from "./StatusBadge";

export default function IssueTable({
  issues,
  members = [],
  onStatusChange = () => {},
  onAssignChange = () => {},
  onDelete = () => {},
  canManageAssignee = false,
  canManageAllStatuses = false,
  projectKey
}) {
  const navigate = useNavigate();
  const { id } = useParams();

  const getUserName = (userId) => {
    const user = members.find((m) => m.id === userId);
    return user ? user.name : `User #${userId}`;
  };

  if (!issues || issues.length === 0) {
    return (
      <div className="empty-state">
        <strong>No issues found</strong>
        Create your first issue to start tracking work.
      </div>
    );
  }

  return (
    <table>
      <thead>
        <tr>
          <th>Issue</th>
          <th>Title</th>
          <th>Status</th>
          <th>Priority</th>
          <th>Reporter</th>
          <th>Assignee</th>
          <th>Actions</th>
        </tr>
      </thead>

      <tbody>
        {issues.map((issue) => (
          <tr key={issue.id}>
            {/* Issue Key */}
            <td style={{ fontWeight: 600 }}>
              {projectKey ? `${projectKey}-${issue.id}` : issue.id}
            </td>

            {/* Title */}
            <td
              style={{ cursor: "pointer", fontWeight: 500 }}
              onClick={() =>
                navigate(`/projects/${id}/issues/${issue.id}`)
              }
            >
              {issue.title}
            </td>

            {/* Status */}
            <td>
              <StatusBadge status={issue.status} />
            </td>

            {/* Priority */}
            <td style={{ textTransform: "capitalize" }}>
              {issue.priority}
            </td>

            {/* Reporter */}
            <td>
              {issue.reporter_name ||
                getUserName(issue.reporter_id)}
            </td>

            {/* Assignee */}
            <td>
              {canManageAssignee ? (
                <select
                  value={issue.assignee_id ?? ""}
                  onChange={(e) =>
                    onAssignChange(
                      issue.id,
                      e.target.value === "" ? null : Number(e.target.value)
                    )
                  }
                >
                  <option value="">Unassigned</option>
                  {members.map((member) => (
                    <option key={member.id} value={member.id}>
                      {member.name}
                    </option>
                  ))}
                </select>
              ) : (
                <span>{issue.assignee_name || "Unassigned"}</span>
              )}
            </td>

            {/* Actions */}
            <td style={{ display: "flex", gap: "8px" }}>
              {canManageAllStatuses ? (
                <select
                  value={issue.status}
                  onChange={(e) =>
                    onStatusChange(issue.id, e.target.value)
                  }
                >
                  <option value="open">Open</option>
                  <option value="in_progress">In Progress</option>
                  <option value="resolved">Resolved</option>
                  <option value="closed">Closed</option>
                </select>
              ) : (
                <StatusBadge status={issue.status} />
              )}

              <button
                className="secondary-btn"
                onClick={() => onDelete(issue.id)}
              >
                Delete
              </button>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
