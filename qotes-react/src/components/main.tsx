import * as React from 'react'
import { BrowserRouter as Router, Link, Route } from 'react-router-dom'
import Hello from './hello'
import Home from './home'
import Topics from './topics'

export default function Main () {
  return (
    <Router>
    <div>
      <ul>
        <li>
          <Link to="/">Qotes</Link>
        </li>
        <li>
          <Link to="/topics">Topics</Link>
        </li>
        <li>
          <Link to="/hello">Hello</Link>
        </li>
      </ul>

      <hr />

      <Route exact={true} path="/" component={Home} />
      <Route path="/topics" component={Topics} />
      <Route path="/hello" component={Hello} />
    </div>
  </Router>
  )
}