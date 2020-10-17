import { view } from "@risingstack/react-easy-state"
import React from "react"
import "./stars.scss"


type StarsProps = {
    rating: number
}

const Stars = (props: StarsProps & { className?: string }) => {
    return <div className={`Stars ${(props.className || "").trim()}`}></div>
}

export default view(Stars)