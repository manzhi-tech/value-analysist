"use client";

import React from 'react';
import { usePathname } from 'next/navigation';
import { FileText } from 'lucide-react';
import styles from './Sidebar.module.css';

interface SidebarProps {
    files: string[];
    currentStep: string;
    onStepChange: (step: string) => void;
    sessionId?: string;
    currentFile?: string;
    onFileSelect?: (file: string) => void;
}

// ... steps array ...
const steps = [
    { id: 'business', label: '1. 商业模式分析' },
    { id: 'mda', label: '2. MD&A 风险分析' },
    { id: 'financial', label: '3. 财务报表分析' },
    { id: 'competitor', label: '4. 竞争对手分析' },
    { id: 'valuation', label: '5. 估值建模' },
];

export default function Sidebar({ files, currentStep, onStepChange, sessionId, currentFile, onFileSelect }: SidebarProps) {
    const handleExport = async () => {
        if (!sessionId) {
            alert("没有可导出的会话");
            return;
        }
        window.open(`http://localhost:8001/api/export/${sessionId}`, '_blank');
    };

    const handleImport = async (e: React.ChangeEvent<HTMLInputElement>) => {
        if (!e.target.files?.[0]) return;
        const file = e.target.files[0];
        const formData = new FormData();
        formData.append("file", file);

        try {
            const res = await fetch('http://localhost:8001/api/import', {
                method: 'POST',
                body: formData
            });
            if (res.ok) {
                const data = await res.json();
                alert("导入成功！页面即将刷新...");
                window.location.reload();
            } else {
                alert("导入失败");
            }
        } catch (err) {
            console.error(err);
            alert("导入出错");
        }
    };


    return (
        <div className={styles.sidebar}>
            {/* ... header ... */}
            <div className={styles.header}>
                <h1 className={styles.title}>价值分析师</h1>
                <p className={styles.subtitle}>巴菲特风格</p>
            </div>

            <div className={styles.content}>
                {/* Uploaded Files Section */}
                <div className={styles.section}>
                    <h2 className={styles.sectionTitle}>上传资料</h2>
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
                                        borderRadius: '0.25rem'
                                    }}
                                >
                                    <FileText size={16} className="mr-2 text-blue-500" />
                                    <span className="truncate">{file.split('/').pop()}</span>
                                </li>
                            );
                        })}
                        {files.length === 0 && (
                            <li className={styles.fileItem} style={{ fontStyle: 'italic', color: '#9ca3af' }}>暂无文件</li>
                        )}
                    </ul>
                </div>
                {/* ... remaining content ... */}


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
                <div className={styles.actions} style={{ marginBottom: '1rem', display: 'flex', gap: '0.5rem' }}>
                    {sessionId && (
                        <button onClick={handleExport} style={{ fontSize: '0.8rem', padding: '0.25rem 0.5rem', cursor: 'pointer' }}>
                            导出状态
                        </button>
                    )}
                    <label style={{ fontSize: '0.8rem', padding: '0.25rem 0.5rem', cursor: 'pointer', background: '#efefef', borderRadius: '2px' }}>
                        导入状态
                        <input type="file" style={{ display: 'none' }} accept=".zip" onChange={handleImport} />
                    </label>
                </div>

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
