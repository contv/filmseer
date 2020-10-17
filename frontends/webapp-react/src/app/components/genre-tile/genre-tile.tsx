import { view } from "@risingstack/react-easy-state"
import React from "react"
import "./genre-tile.scss"


type GenreTileProps = {
    text: string,
    onClick?: () => void 
}

const GenreTile = (props: GenreTileProps & { className?: string }) => {
    return <div className={`GenreTile ${(props.className || "").trim()}`}></div>
}


export default view(GenreTile)