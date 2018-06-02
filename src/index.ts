import React from 'react'

type Props = {
    onClick(e: MouseEvent<HTMLElement>): void
    children?: ReactNode
}

const Button = ({ onClick: handleClick, children }) => (
    <button onClick={handleClick}>{children}</button>
)
