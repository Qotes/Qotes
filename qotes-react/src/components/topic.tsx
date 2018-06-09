import * as React from 'react'

export default function Topic ({match}: {match: any}) {
  return (
    <div>
      <h3>{match.params.topicId}</h3>
    </div>
  )
}
