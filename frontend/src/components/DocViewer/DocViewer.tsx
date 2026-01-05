"use client";

import { Document, Page, pdfjs } from 'react-pdf';
import React, { useState, useEffect } from 'react';
import 'react-pdf/dist/Page/AnnotationLayer.css';
import 'react-pdf/dist/Page/TextLayer.css';
import styles from './DocViewer.module.css';

// Set worker source
pdfjs.GlobalWorkerOptions.workerSrc = `//unpkg.com/pdfjs-dist@${pdfjs.version}/build/pdf.worker.min.mjs`;

interface DocViewerProps {
    filePath?: string;
    highlightRect?: [number, number, number, number];
    targetPage?: number;
}

export default function DocViewer({ filePath, highlightRect, targetPage = 1 }: DocViewerProps) {
    const [numPages, setNumPages] = useState<number>(0);
    const [currentPage, setCurrentPage] = useState<number>(targetPage);

    useEffect(() => {
        if (targetPage) setCurrentPage(targetPage);
    }, [targetPage]);

    function onDocumentLoadSuccess({ numPages }: { numPages: number }) {
        setNumPages(numPages);
    }

    return (
        <div className={styles.container}>
            <div className={styles.toolbar}>
                <span className={styles.fileName}>
                    {filePath ? filePath.split('/').pop() : "No document selected"}
                </span>
                <div className={styles.controls}>
                    <button
                        className={styles.pageBtn}
                        disabled={currentPage <= 1}
                        onClick={() => setCurrentPage(p => p - 1)}
                    >Prev</button>
                    <span className={styles.pageInfo}>Page {currentPage} of {numPages}</span>
                    <button
                        className={styles.pageBtn}
                        disabled={currentPage >= numPages}
                        onClick={() => setCurrentPage(p => p + 1)}
                    >Next</button>
                </div>
            </div>

            <div className={styles.canvasContainer}>
                {filePath ? (
                    <Document
                        file={filePath}
                        onLoadSuccess={onDocumentLoadSuccess}
                        className="shadow-lg"
                    >
                        <Page
                            pageNumber={currentPage}
                            width={600}
                            renderTextLayer={true}
                            renderAnnotationLayer={true}
                        />
                    </Document>
                ) : (
                    <div className={styles.emptyState}>Please upload and select a document</div>
                )}
            </div>
        </div>
    );
}
