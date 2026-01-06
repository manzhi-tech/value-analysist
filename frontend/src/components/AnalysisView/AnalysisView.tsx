"use client";

import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Citation } from '@/types';
import styles from './AnalysisView.module.css';

interface AnalysisViewProps {
    content: string;
    onCitationClick: (citation: Citation) => void;
    isLoading?: boolean;
}

export default function AnalysisView({ content, onCitationClick, isLoading }: AnalysisViewProps) {

    const renderContent = (text: string) => {
        // Matches [[Page 6]], [[Source: Page 6]], [Page 6], [Page6]
        const regex = /\[\[?(?:Source:\s*)?Page\s*(\d+)\]?\]/gi;
        const parts = text.split(regex);

        if (parts.length === 1) return text;

        return parts.map((part, i) => {
            if (i % 2 === 1) {
                const pageNum = parseInt(part);
                return (
                    <button
                        key={i}
                        onClick={() => onCitationClick({ page: pageNum })}
                        className={styles.citationBtn}
                    >
                        [Page {pageNum}]
                    </button>
                );
            }
            return part;
        });
    };

    return (
        <div className={styles.container}>
            {isLoading && (
                <div className={styles.loading}>
                    <div className={styles.spinner}></div>
                    <span>Analyzing...</span>
                </div>
            )}

            <div className={styles.markdown}>
                <ReactMarkdown
                    remarkPlugins={[remarkGfm]}
                    components={{
                        p: ({ node, children }) => {
                            return (
                                <p>
                                    {React.Children.map(children, child => {
                                        if (typeof child === 'string') {
                                            return renderContent(child);
                                        }
                                        return child;
                                    })}
                                </p>
                            )
                        }
                    }}
                >
                    {content}
                </ReactMarkdown>
            </div>

            {!content && !isLoading && (
                <div className={styles.emptyState}>
                    Waiting for analysis to start...
                </div>
            )}
        </div>
    );
}
