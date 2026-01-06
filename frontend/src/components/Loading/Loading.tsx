import React, { useState, useEffect } from 'react';
import styles from './Loading.module.css';

const MESSAGES = [
    "正在深入阅读文档...",
    "正在解析关键数据...",
    "正在构建思维导图...",
    "正在交叉验证信息来源...",
    "正在生成专业见解...",
    "正在组织最终报告..."
];

export default function Loading() {
    const [messageIndex, setMessageIndex] = useState(0);

    useEffect(() => {
        const interval = setInterval(() => {
            setMessageIndex((prev) => (prev + 1) % MESSAGES.length);
        }, 3000);

        return () => clearInterval(interval);
    }, []);

    return (
        <div className={styles.container}>
            <div className={styles.loader}>
                <div className={styles.circle}></div>
                <div className={styles.circleInner}></div>
            </div>
            <div className={styles.textContainer}>
                <div key={messageIndex} className={styles.text}>
                    {MESSAGES[messageIndex]}
                </div>
            </div>
            <div className={styles.subText}>
                AI 智能助手正在努力工作中
            </div>
        </div>
    );
}
