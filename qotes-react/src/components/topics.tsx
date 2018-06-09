import * as React from 'react'
import { Link, Route } from 'react-router-dom'
import Topic from './topic'


export default function Topics ({ match }: { match: any }) {
  return (
    <div>
      <h2>Topics</h2>
      <ul>
        <li>
          <Link to={`${match.url}/rendering`}>Rendering with React</Link>
        </li>
        <li>
          <Link to={`${match.url}/components`}>Components</Link>
        </li>
        <li>
          <Link to={`${match.url}/props-v-state`}>333</Link>
        </li>
      </ul>

      <Route path={`${match.url}/:topicId`} component={Topic} />
      <Route
        exact={true}
        path={match.url}
        // tslint:disable-next-line:jsx-no-lambda
        render={() => <h3>Please select a topic.</h3>} // https://stackoverflow.com/questions/36677733/why-shouldnt-jsx-props-use-arrow-functions-or-bind
      />
    </div>
  )
}
