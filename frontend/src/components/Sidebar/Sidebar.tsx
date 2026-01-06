"use client";

import React from 'react';
import { usePathname } from 'next/navigation';
import { FileText } from 'lucide-react';
import styles from './Sidebar.module.css';

import { AnalysisSession } from '@/types';

interface SidebarProps {
    files: string[];
    currentStep: string;
    onStepChange: (step: string) => void;
    sessionId?: string;
    currentFile?: string;
    onFileSelect?: (file: string) => void;
    onDeleteFile?: (file: string) => void;

    // New props
    onUploadFile?: (e: React.ChangeEvent<HTMLInputElement>) => void;
    onBack?: () => void;
}

// ... steps array ...
const steps = [
    { id: 'business', label: '1. 商业模式分析' },
    { id: 'mda', label: '2. MD&A 风险分析' },
    { id: 'financial', label: '3. 财务报表分析' },
    { id: 'competitor', label: '4. 竞争对手分析' },
    { id: 'valuation', label: '5. 估值建模' },
];

export default function Sidebar({
    files,
    currentStep,
    onStepChange,
    sessionId,
    currentFile,
    onFileSelect,
    onDeleteFile,
    onUploadFile,
    onBack
}: SidebarProps) {

    // Removed handleExport and handleImport as per user request

    return (
        <div className={styles.sidebar}>
            {/* ... header ... */}
            <div className={styles.header}>
                <div
                    onClick={onBack}
                    style={{ cursor: 'pointer', display: 'flex', alignItems: 'center', marginBottom: '0.5rem', color: '#6b7280', fontSize: '0.85rem' }}
                >
                    ← 返回列表
                </div>
                <h1 className={styles.title}>价值分析师</h1>
                <p className={styles.subtitle}>巴菲特风格</p>
            </div>

            <div className={styles.content}>
                {/* Uploaded Files Section */}
                <div className={styles.section}>
                    <div className="flex justify-between items-center mb-2">
                        <h2 className={styles.sectionTitle} style={{ marginBottom: 0 }}>研究资料</h2>
                        <label className="cursor-pointer text-blue-500 hover:text-blue-700 text-xs">
                            + 添加
                            <input
                                type="file"
                                className="hidden"
                                style={{ display: 'none' }}
                                onChange={onUploadFile}
                                accept=".pdf"
                            />
                        </label>
                    </div>

                    <ul className={styles.list}>
                        {files.map((file, idx) => {
                            const isSelected = currentFile === file;
                            return (
                                <li key={idx}
                                    className={styles.fileItem}
                                    onClick={() => onFileSelect && onFileSelect(file)}
                                    style={{
                                        cursor: 'pointer',
                                        backgroundColor: isSelected ? '#e5e7eb' : 'transparent',
                                        borderRadius: '0.25rem',
                                        display: 'flex',
                                        justifyContent: 'space-between',
                                        alignItems: 'center'
                                    }}
                                >
                                    <div className="flex items-center overflow-hidden">
                                        <FileText size={16} className="mr-2 text-blue-500 flex-shrink-0" />
                                        <span className="truncate">{file.split('/').pop()}</span>
                                    </div>
                                    <button
                                        onClick={(e) => {
                                            e.stopPropagation();
                                            if (onDeleteFile) onDeleteFile(file);
                                        }}
                                        className="text-gray-400 hover:text-red-500 ml-2"
                                        title="删除文件"
                                    >
                                        ×
                                    </button>
                                </li>
                            );
                        })}
                        {files.length === 0 && (
                            <li className={styles.fileItem} style={{ fontStyle: 'italic', color: '#9ca3af' }}>暂无文件</li>
                        )}
                    </ul>
                </div>

                {/* Analysis Steps Section */}
                <div className={styles.section}>
                    <h2 className={styles.sectionTitle}>分析流程</h2>
                    <ul className={styles.list}>
                        {steps.map((step) => {
                            const isActive = currentStep === step.id;
                            return (
                                <li key={step.id} onClick={() => onStepChange(step.id)} style={{ cursor: 'pointer' }}>
                                    <div className={`${styles.stepItem} ${isActive ? styles.stepActive : ''}`}>
                                        <div className={`${styles.indicator} ${isActive ? styles.indicatorActive : ''}`} />
                                        <span className={styles.stepLabel}>{step.label}</span>
                                    </div>
                                </li>
                            );
                        })}
                    </ul>
                </div>
            </div>

            <div className={styles.footer}>
                <div className={styles.userProfile}>
                    <div className={styles.avatar}>U</div>
                    <div className={styles.userInfo}>
                        <p className={styles.userName}>User</p>
                        <p className={styles.userPlan}>Free Plan</p>
                    </div>
                </div>
            </div>
        </div>
    );
}

