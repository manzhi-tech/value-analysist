"use client";

import React from 'react';
import { AnalysisSession } from '@/types';
import styles from './SessionList.module.css';

interface SessionListProps {
    sessions: AnalysisSession[];
    onSelect: (session: AnalysisSession) => void;
    onUpload: (e: React.ChangeEvent<HTMLInputElement>) => void;
}

export default function SessionList({ sessions, onSelect, onUpload }: SessionListProps) {

    const formatDate = (dateStr: string) => {
        try {
            const date = new Date(dateStr);
            return new Intl.DateTimeFormat('zh-CN', {
                year: 'numeric',
                month: 'short',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            }).format(date);
        } catch (e) {
            return dateStr;
        }
    };

    const getStatusLabel = (session: AnalysisSession) => {
        // Aggregate status or just check main status
        if (session.valuation_status === 'COMPLETED') return { label: '已完成', class: styles.statusCompleted };
        if (session.business_status === 'RUNNING' || session.financial_status === 'RUNNING') return { label: '分析中', class: styles.statusRunning };
        if (session.business_status === 'FAILED') return { label: '失败', class: styles.statusFailed };
        if (session.business_status === 'COMPLETED') return { label: '进行中', class: styles.statusRunning };
        return { label: '待处理', class: styles.statusPending };
    };

    return (
        <div className={styles.container}>
            <div className={styles.header}>
                <div>
                    <h1 className={styles.title}>我的研究</h1>
                    <p className={styles.subtitle}>所有投资分析任务概览</p>
                </div>
            </div>

            <div className={styles.grid}>
                {/* New Analysis Card */}
                <label className={`${styles.card} ${styles.newCard}`}>
                    <div style={{ width: 48, height: 48, borderRadius: '50%', background: 'white', display: 'flex', alignItems: 'center', justifyContent: 'center', border: '1px solid #e5e7eb', boxShadow: '0 2px 4px rgba(0,0,0,0.05)' }}>
                        <span style={{ fontSize: '24px', fontWeight: 300 }}>+</span>
                    </div>
                    <span style={{ fontWeight: 600, fontSize: '1.1rem' }}>新建研究任务</span>
                    <input
                        type="file"
                        style={{ display: 'none' }}
                        onChange={onUpload}
                        accept=".pdf"
                    />
                </label>

                {/* Session Cards */}
                {sessions.map((session) => {
                    const status = getStatusLabel(session);
                    const displayTitle = session.company_name || session.file_name || "未命名研究";

                    return (
                        <div
                            key={session.id}
                            className={styles.card}
                            onClick={() => onSelect(session)}
                        >
                            <div className={styles.cardContent}>
                                <div className={styles.cardIcon}>
                                    {/* Simple Document Icon */}
                                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                        <path d="M14 2H6C5.46957 2 4.96086 2.21071 4.58579 2.58579C4.21071 2.96086 4 3.46957 4 4V20C4 20.5304 4.21071 21.0391 4.58579 21.4142C4.96086 21.7893 5.46957 22 6 22H18C18.5304 22 19.0391 21.7893 19.4142 21.4142C19.7893 21.0391 20 20.5304 20 20V8L14 2Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                                        <path d="M14 2V8H20" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                                        <path d="M16 13H8" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                                        <path d="M16 17H8" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                                        <path d="M10 9H8" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                                    </svg>
                                </div>
                                <h3 className={styles.cardTitle}>{displayTitle}</h3>
                            </div>

                            <div className={styles.cardFooter}>
                                <span className={styles.cardDate}>
                                    {session.created_at.substring(0, 10)}
                                </span>
                                <span className={`${styles.status} ${status.class}`}>
                                    {status.label}
                                </span>
                            </div>
                        </div>
                    );
                })}
            </div>
        </div>
    );
}
