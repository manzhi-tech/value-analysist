"use client";

import React from 'react';
import Loading from '../Loading/Loading';
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
        // Matches [[Page 6]], [[Source: Page 6]], [Page 6], [Page 4-5], [Page 4, Page 5], [Page 4-5, Page 36-37]
        // Captures the entire citation block
        const regex = /(\[\[?(?:Source:\s*)?Page\s*(?:[\d\-\s,]+(?:Page)?)*\]?\])/gi;
        const parts = text.split(regex);

        if (parts.length === 1) return text;

        return parts.map((part, i) => {
            // Check if this part is a citation block
            if (part.match(regex)) {
                // Extract all page numbers/ranges from the block
                // Matches "4", "4-5", "36-37"
                const pageNumRegex = /(\d+(?:-\d+)?)/g;
                const matches = [...part.matchAll(pageNumRegex)];

                if (matches.length > 0) {
                    return (
                        <span key={i} className={styles.citationGroup}>
                            {matches.map((match, index) => {
                                const pageStr = match[1];
                                const startPage = parseInt(pageStr.split('-')[0]);
                                return (
                                    <button
                                        key={index}
                                        onClick={() => onCitationClick({ page: startPage })}
                                        className={styles.citationBtn}
                                        style={{ marginLeft: index > 0 ? '4px' : '0' }}
                                    >
                                        [Page {pageStr}]
                                    </button>
                                );
                            })}
                        </span>
                    );
                }
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

    if (isLoading) {
        return <Loading />;
    }

    return (
        <div className={styles.container}>

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
