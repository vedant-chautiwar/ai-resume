import { useState } from 'react'
import JobForm from '../components/JobForm'
import MatchButton from '../components/MatchButton'
import MatchResult from '../components/MatchResult'
import Navbar from '../components/Navbar'
import ResumeUpload from '../components/ResumeUpload'
import api from '../api/axios'

function getFriendlyError(error, fallbackMessage) {
  if (!error.response) {
    return 'Unable to connect to the backend.'
  }

  if (typeof error.response.data?.detail === 'string') {
    return error.response.data.detail
  }

  return fallbackMessage
}

function Dashboard() {
  const [selectedFile, setSelectedFile] = useState(null)
  const [resumeUploaded, setResumeUploaded] = useState(false)
  const [resumeId, setResumeId] = useState('')
  const [jobTitle, setJobTitle] = useState('')
  const [jobDescription, setJobDescription] = useState('')
  const [jobId, setJobId] = useState('')
  const [uploading, setUploading] = useState(false)
  const [creatingJob, setCreatingJob] = useState(false)
  const [analyzing, setAnalyzing] = useState(false)
  const [matchResult, setMatchResult] = useState(null)
  const [errorMessage, setErrorMessage] = useState('')
  const [successMessage, setSuccessMessage] = useState('')

  const canAnalyze = resumeId && jobId
  const isBusy = uploading || creatingJob || analyzing

  async function handleResumeSelect(file) {
    if (!file) {
      return
    }

    if (file.type !== 'application/pdf') {
      setErrorMessage('Please upload a valid PDF resume.')
      return
    }

    setUploading(true)
    setErrorMessage('')
    setSuccessMessage('')
    setSelectedFile(file)
    setMatchResult(null)

    const formData = new FormData()
    formData.append('file', file)

    try {
      const response = await api.post('/api/resumes/upload', formData)

      setResumeId(response.data.resume_id)
      setResumeUploaded(true)
      setSuccessMessage('Resume uploaded successfully.')
    } catch (error) {
      setSelectedFile(null)
      setResumeId('')
      setResumeUploaded(false)
      setErrorMessage(getFriendlyError(error, 'Resume upload failed.'))
    } finally {
      setUploading(false)
    }
  }

  function handleRemoveResume() {
    setSelectedFile(null)
    setResumeUploaded(false)
    setResumeId('')
    setMatchResult(null)
    setSuccessMessage('')
  }

  function handleJobTitleChange(value) {
    setJobTitle(value)
    setJobId('')
    setMatchResult(null)
    setSuccessMessage('')
  }

  function handleJobDescriptionChange(value) {
    setJobDescription(value)
    setJobId('')
    setMatchResult(null)
    setSuccessMessage('')
  }

  async function handleJobSubmit(event) {
    event.preventDefault()

    if (!jobTitle.trim() || !jobDescription.trim()) {
      setErrorMessage('Please enter both job title and job description.')
      return
    }

    setCreatingJob(true)
    setErrorMessage('')
    setSuccessMessage('')
    setMatchResult(null)

    try {
      const response = await api.post('/api/jobs/', {
        title: jobTitle,
        description: jobDescription
      })

      setJobId(response.data.job_id)
      setSuccessMessage('Job description saved successfully.')
    } catch (error) {
      setJobId('')
      setErrorMessage(getFriendlyError(error, 'Job creation failed.'))
    } finally {
      setCreatingJob(false)
    }
  }

  async function handleAnalyze() {
    if (!resumeId) {
      setErrorMessage('Please upload a resume first.')
      return
    }

    if (!jobId) {
      setErrorMessage('Please add the job description first.')
      return
    }

    if (!canAnalyze || analyzing) {
      return
    }

    setAnalyzing(true)
    setErrorMessage('')
    setSuccessMessage('')
    setMatchResult(null)

    try {
      const response = await api.post('/api/matches', {
        resume_id: resumeId,
        job_id: jobId
      })

      setMatchResult(response.data)
      setSuccessMessage('Match analysis completed.')
    } catch (error) {
      setErrorMessage(getFriendlyError(error, 'Match generation failed.'))
    } finally {
      setAnalyzing(false)
    }
  }

  return (
    <div className="app-shell">
      <Navbar />

      <main className="dashboard">
        <section className="hero-section">
          <div>
            <p className="eyebrow">AI Resume Intelligence</p>
            <h1>AI Resume Matcher</h1>
            <p className="hero-text">
              Upload your resume and compare it with a job description using AI.
            </p>
          </div>
          <div className="status-panel" aria-label="Workflow progress">
            <span className={resumeUploaded ? 'step is-done' : 'step'}>Resume</span>
            <span className={jobId ? 'step is-done' : 'step'}>Job</span>
            <span className={matchResult ? 'step is-done' : 'step'}>Match</span>
          </div>
        </section>

        {errorMessage && <div className="message error">{errorMessage}</div>}
        {successMessage && <div className="message success">{successMessage}</div>}

        <section className="dashboard-grid">
          <ResumeUpload
            selectedFile={selectedFile}
            resumeUploaded={resumeUploaded}
            uploading={uploading}
            disabled={isBusy}
            onResumeSelect={handleResumeSelect}
            onRemoveResume={handleRemoveResume}
          />

          <JobForm
            jobTitle={jobTitle}
            jobDescription={jobDescription}
            jobSaved={Boolean(jobId)}
            creatingJob={creatingJob}
            disabled={uploading || creatingJob || analyzing}
            onJobTitleChange={handleJobTitleChange}
            onJobDescriptionChange={handleJobDescriptionChange}
            onSubmit={handleJobSubmit}
          />
        </section>

        <section className="match-panel">
          <div>
            <p className="section-label">Analyze Match</p>
            <h2>Ready to compare?</h2>
            <p>
              The button becomes active after a PDF resume and job description are added.
            </p>
          </div>

          <MatchButton
            disabled={!canAnalyze || uploading || creatingJob}
            loading={analyzing}
            onClick={handleAnalyze}
          />
        </section>

        <MatchResult result={matchResult} loading={analyzing} />
      </main>
    </div>
  )
}

export default Dashboard
