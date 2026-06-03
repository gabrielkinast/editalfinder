export default function ScientificToast({ toast }) {
  if (!toast?.message) return null;
  const type = toast.type || 'success';
  return (
    <div className={`scientific-toast scientific-toast--${type}`} role="status" aria-live="polite">
      {toast.message}
    </div>
  );
}
