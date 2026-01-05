"use client";

import Sidebar from '@/components/Sidebar/Sidebar';
import AnalysisView from '@/components/AnalysisView/AnalysisView';
import dynamic from 'next/dynamic';
import { useState, useEffect } from 'react';

const DocViewer = dynamic(() => import('@/components/DocViewer/DocViewer'), {
  ssr: false,
  loading: () => <p>加载 PDF 查看器...</p>
});
import { AnalysisSession, Citation } from '@/types';
import styles from './page.module.css';

export default function Home() {
  // Map step IDs to backend fields
  const stepMapping: Record<string, { status: keyof AnalysisSession, result: keyof AnalysisSession }> = {
    'business': { status: 'business_status', result: 'business_analysis_result' },
    'mda': { status: 'mda_status', result: 'mda_analysis_result' },
    'financial': { status: 'financial_status', result: 'financial_analysis_result' },
    'competitor': { status: 'competitor_status', result: 'competitor_analysis_result' },
    'valuation': { status: 'valuation_status', result: 'valuation_result' },
  };

  const [session, setSession] = useState<AnalysisSession | null>(null);
  const [currentFile, setCurrentFile] = useState<string | undefined>(undefined);
  const [currentStep, setCurrentStep] = useState<string>('business');

  const [targetPage, setTargetPage] = useState<number>(1);
  const [highlightRect, setHighlightRect] = useState<[number, number, number, number] | undefined>(undefined);

  // Poll for status
  useEffect(() => {
    if (!session) return;

    const checkStatus = async () => {
      try {
        const res = await fetch(`http://localhost:8001/api/session/${session.id}`);
        if (res.ok) {
          const data = await res.json();
          // Backend returns file_paths_json which contains absolute paths
          // We must convert them to /static/ relative URLs for the frontend
          if (data.file_paths_json) {
            try {
              const paths = JSON.parse(data.file_paths_json);

              const staticPaths: string[] = [];
              if (Array.isArray(paths)) {
                paths.forEach((absolutePath: string) => {
                  const uploadIndex = absolutePath.indexOf('/uploads/');
                  let staticPath = '';
                  if (uploadIndex !== -1) {
                    const relativePath = absolutePath.substring(uploadIndex + '/uploads/'.length);
                    staticPath = `/static/${relativePath}`;
                  } else {
                    const parts = absolutePath.split('/');
                    const filename = parts[parts.length - 1];
                    staticPath = `/static/${filename}`;
                  }
                  staticPaths.push(staticPath);
                });
              }
              data.file_paths = staticPaths;

              // Defaults
              if (staticPaths.length > 0) {
                data.file_path = staticPaths[0]; // Legacy support
              }
            } catch (e) {
              // ignore parse error
            }
          }

          setSession(data);

          // Auto-select first file if not set
          if (!currentFile && data.file_paths && data.file_paths.length > 0) {
            setCurrentFile(data.file_paths[0]);
          }
        }
      } catch (e) {
        console.error("Polling error", e);
      }
    };

    // Immediate check
    checkStatus();

    // Set interval
    const interval = setInterval(checkStatus, 3000); // 3s polling
    return () => clearInterval(interval);
  }, [session?.id]); // Only recreate if session ID changes

  // Derived state for current step
  const currentStatus = session ? session[stepMapping[currentStep].status] as string : 'PENDING';
  const currentResult = session ? session[stepMapping[currentStep].result] as string : '';
  const isAnalyzing = currentStatus === 'RUNNING';

  const handleCitationClick = (citation: Citation) => {
    setTargetPage(citation.page);
    if (citation.rect) setHighlightRect(citation.rect);
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files?.[0]) return;
    const file = e.target.files[0];
    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch('http://localhost:8001/api/upload', {
        method: 'POST',
        body: formData
      });
      if (!res.ok) throw new Error('Upload failed');
      const data = await res.json();

      const staticPath = `/static/${file.name}`;

      // Initialize a basic session object locally before first poll
      setSession({
        id: data.session_id,
        file_path: staticPath,
        file_paths: [staticPath], // Start with this one
        file_name: file.name,
        created_at: new Date().toISOString(),
        // Defaults
        business_status: 'PENDING', mda_status: 'PENDING', financial_status: 'PENDING',
        competitor_status: 'PENDING', valuation_status: 'PENDING',
      } as AnalysisSession);
      setCurrentFile(staticPath);
    } catch (err) {
      console.error(err);
      alert("上传失败，请检查后台连接。");
    }
  };

  const runAnalysis = async () => {
    if (!session) return;
    try {
      await fetch(`http://localhost:8001/api/analyze/${session.id}/${currentStep}`, {
        method: 'POST'
      });
    } catch (err) {
      console.error(err);
      alert("启动分析失败");
    }
  };

  // Update step names for UI display
  const stepTitles: Record<string, string> = {
    'business': '商业模式分析',
    'mda': 'MD&A 风险分析',
    'financial': '财务报表分析',
    'competitor': '竞争对手分析',
    'valuation': '估值建模'
  };

  return (
    <main className={styles.container}>
      <Sidebar
        files={session?.file_paths || (session?.file_path ? [session.file_path] : [])}
        currentStep={currentStep}
        onStepChange={setCurrentStep}
        sessionId={session?.id}
        currentFile={currentFile}
        onFileSelect={setCurrentFile}
      />

      <div className={styles.mainContent}>
        <div className={styles.splitPane}>
          {/* Left: Analysis */}
          <div className={styles.leftPanel}>
            <div className={styles.panelHeader}>
              <h2 className={styles.panelTitle}>{stepTitles[currentStep]}</h2>
              <div>
                {!session ? (
                  <label className={styles.uploadLabel}>
                    上传年报 (PDF)
                    <input type="file" className="hidden" style={{ display: 'none' }} onChange={handleFileUpload} accept=".pdf" />
                  </label>
                ) : (
                  <button
                    onClick={runAnalysis}
                    disabled={isAnalyzing}
                    className={`${styles.actionButton} ${isAnalyzing ? 'opacity-50 cursor-not-allowed' : ''}`}
                    style={{ backgroundColor: isAnalyzing ? '#9ca3af' : undefined }}
                  >
                    {isAnalyzing ? '分析进行中...' : (currentStatus === 'COMPLETED' ? '重新分析' : '开始分析')}
                  </button>
                )}
              </div>
            </div>
            <AnalysisView
              content={currentResult || ""}
              onCitationClick={handleCitationClick}
              isLoading={isAnalyzing}
            />
          </div>

          {/* Right: Doc Viewer */}
          <div className={styles.rightPanel}>
            <DocViewer
              filePath={currentFile ? `http://localhost:8001${currentFile}` : undefined}
              targetPage={targetPage}
              highlightRect={highlightRect}
            />
          </div>
        </div>
      </div>
    </main>
  );
}
