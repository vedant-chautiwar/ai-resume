function ResumeUpload({
  selectedFile,
  resumeUploaded,
  uploading,
  disabled,
  onResumeSelect,
  onRemoveResume
}) {
  function handleFileChange(event) {
    const file = event.target.files[0]

    if (file) {
      onResumeSelect(file)
    }
  }

  return (
    <article className="card">
      <div className="card-header">
        <div>
          <p className="section-label">Resume Section</p>
          <h2>Upload Resume</h2>
        </div>
        <span className={resumeUploaded ? 'badge success' : 'badge'}>
          {uploading ? 'Uploading' : resumeUploaded ? 'Uploaded' : 'PDF only'}
        </span>
      </div>

      <label className={disabled ? 'upload-box is-disabled' : 'upload-box'}>
        <input
          type="file"
          accept="application/pdf"
          disabled={disabled}
          onChange={handleFileChange}
        />
        <span className="upload-icon">PDF</span>
        <strong>
          {uploading
            ? 'Uploading...'
            : resumeUploaded
              ? 'Resume uploaded successfully'
              : 'Upload your PDF resume'}
        </strong>
        <small>
          {selectedFile ? selectedFile.name : 'Choose a PDF file from your computer'}
        </small>
      </label>

      {resumeUploaded && (
        <div className="file-row">
          <div>
            <p>{selectedFile.name}</p>
            <span>Ready for matching</span>
          </div>
          <button
            type="button"
            className="ghost-button"
            disabled={disabled}
            onClick={onRemoveResume}
          >
            Remove
          </button>
        </div>
      )}
    </article>
  )
}

export default ResumeUpload
