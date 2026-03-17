export default function Modal({ children, onClose, className = '' }) {
  return (
    <div className="modal" style={{ display: 'flex' }}>
      <div className={`modal-content ${className}`}>
        <span className="close-modal" onClick={onClose}>&times;</span>
        {children}
      </div>
    </div>
  );
}
