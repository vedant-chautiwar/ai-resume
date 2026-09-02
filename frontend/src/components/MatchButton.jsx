function MatchButton({ disabled, loading, onClick }) {
  return (
    <button
      type="button"
      className="primary-button"
      disabled={disabled || loading}
      onClick={onClick}
    >
      {loading ? 'Analyzing...' : 'Analyze Match'}
    </button>
  )
}

export default MatchButton
