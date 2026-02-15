export default function StatusBadge({ status }) {
  const getColor = () => {
    switch (status) {
      case "open":
        return "#2563eb";
      case "in_progress":
        return "#f59e0b";
      case "resolved":
        return "#10b981";
      case "closed":
        return "#6b7280";
      default:
        return "#9ca3af";
    }
  };

  const formatLabel = (value) => {
    return value.replace("_", " ").replace(/\b\w/g, (c) => c.toUpperCase());
  };

  return (
    <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
      <span
        style={{
          width: "8px",
          height: "8px",
          borderRadius: "50%",
          backgroundColor: getColor()
        }}
      />
      <span>{formatLabel(status)}</span>
    </div>
  );
}
