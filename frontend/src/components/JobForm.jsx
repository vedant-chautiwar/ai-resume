function JobForm({
  jobTitle,
  jobDescription,
  jobSaved,
  creatingJob,
  disabled,
  onJobTitleChange,
  onJobDescriptionChange,
  onSubmit
}) {
  return (
    <article className="card">
      <div className="card-header">
        <div>
          <p className="section-label">Job Description Section</p>
          <h2>Enter Job Details</h2>
        </div>
        {jobSaved && <span className="badge success">Saved</span>}
      </div>

      <form className="job-form" onSubmit={onSubmit}>
        <label>
          Job Title
          <input
            type="text"
            value={jobTitle}
            placeholder="Frontend Developer"
            disabled={disabled}
            onChange={(event) => onJobTitleChange(event.target.value)}
          />
        </label>

        <label>
          Job Description
          <textarea
            value={jobDescription}
            placeholder="Paste the job description here..."
            rows="8"
            disabled={disabled}
            onChange={(event) => onJobDescriptionChange(event.target.value)}
          />
        </label>

        <button type="submit" className="secondary-button" disabled={disabled}>
          {creatingJob ? 'Creating Job...' : 'Add Job Description'}
        </button>
      </form>
    </article>
  )
}

export default JobForm
