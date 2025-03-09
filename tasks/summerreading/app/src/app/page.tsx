"use client";

import { useEffect, useState } from "react";
import LICENSE from "./license";

export default function Home() {
    let [content, setContent] = useState("");

    useEffect(() => {
        let currentLine = 0;
        let timeoutId: number;

        let renderNextLine = () => {
            setContent(LICENSE.slice(currentLine, currentLine + 20).join("\n"));
            currentLine++;
            timeoutId = window.setTimeout(() => {
                renderNextLine();
            }, 2000);
        };
        renderNextLine();

        return () => clearTimeout(timeoutId);
    }, []);

    return (
        <main>
            <h2>License Agreement</h2>
            <p>Please read the following license agreement carefully.</p>

            <textarea value={content} readOnly />
        </main>
    );
}
