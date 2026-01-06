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

    const processChildren = (children: React.ReactNode) => {
        return React.Children.map(children, child => {
            if (typeof child === 'string') {
                return renderContent(child);
            }
            return child;
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
                        p: ({ node, children, ...props }) => <p {...props}>{processChildren(children)}</p>,
                        li: ({ node, children, ...props }) => <li {...props}>{processChildren(children)}</li>,
                        h1: ({ node, children, ...props }) => <h1 {...props}>{processChildren(children)}</h1>,
                        h2: ({ node, children, ...props }) => <h2 {...props}>{processChildren(children)}</h2>,
                        h3: ({ node, children, ...props }) => <h3 {...props}>{processChildren(children)}</h3>,
                        h4: ({ node, children, ...props }) => <h4 {...props}>{processChildren(children)}</h4>,
                        h5: ({ node, children, ...props }) => <h5 {...props}>{processChildren(children)}</h5>,
                        h6: ({ node, children, ...props }) => <h6 {...props}>{processChildren(children)}</h6>,
                        blockquote: ({ node, children, ...props }) => <blockquote {...props}>{processChildren(children)}</blockquote>,
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
