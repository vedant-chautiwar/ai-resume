function SkillList({ title, skills, tone, prefix }) {
  const safeSkills = skills || []

  return (
    <div className="skill-group">
      <h3>{title}</h3>
      <div className="skills">
        {safeSkills.map((skill) => (
          <span className={`skill ${tone}`} key={skill}>
            {prefix && <span className="skill-prefix">{prefix}</span>} {skill}
          </span>
        ))}
        {safeSkills.length === 0 && <span className="empty-skill">No items found</span>}
      </div>
    </div>
  )
}

function MatchResult({ result, loading }) {
  if (loading) {
    return (
      <section className="result-card loading-card">
        <div className="loader"></div>
        <div>
          <h2>Analyzing resume match</h2>
          <p>Checking resume strengths against the job description.</p>
        </div>
      </section>
    )
  }

  if (!result) {
    return (
      <section className="result-card empty-card">
        <p className="section-label">Result Section</p>
        <h2>Match results will appear here</h2>
        <p>
          Add a resume and job description, then run the analysis to see the result.
        </p>
      </section>
    )
  }

  const strongMatches = result.strong_matches || result.matched_skills || []
  const partialMatches = result.partial_matches || result.weak_skills || []
  const skillGaps = result.skill_gaps || result.missing_skills || []
  const suggestions = result.improvement_suggestions || []

  return (
    <section className="result-card">
      <div className="result-top">
        <div>
          <p className="section-label">Match Score</p>
          <h2>{result.score}%</h2>
        </div>
        <div className="score-ring" style={{ '--score': `${result.score}%` }}>
          <span>{result.score}</span>
        </div>
      </div>

      {result.recommendation && (
        <div className="recommendation-block">
          <h3>Recommendation</h3>
          <p className="recommendation-badge">{result.recommendation}</p>
        </div>
      )}

      <div className="summary-block">
        <h3>Candidate Summary</h3>
        <p>{result.summary}</p>
      </div>

      <SkillList
        title="Strong Matches"
        skills={strongMatches}
        tone="matched"
        prefix="✓"
      />
      <SkillList
        title="Partial Matches"
        skills={partialMatches}
        tone="weak"
        prefix="~"
      />
      <SkillList
        title="Skill Gaps"
        skills={skillGaps}
        tone="missing"
        prefix="✗"
      />

      {suggestions.length > 0 && (
        <div className="suggestions-block">
          <h3>How To Improve</h3>
          <ol className="suggestions-list">
            {suggestions.map((item, idx) => (
              <li key={idx}>{item}</li>
            ))}
          </ol>
        </div>
      )}
    </section>
  )
}

export default MatchResult
