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

import SessionList from '@/components/SessionList/SessionList';

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
  const [sessions, setSessions] = useState<AnalysisSession[]>([]);
  const [currentFile, setCurrentFile] = useState<string | undefined>(undefined);
  const [currentStep, setCurrentStep] = useState<string>('business');

  const [targetPage, setTargetPage] = useState<number>(1);
  const [highlightRect, setHighlightRect] = useState<[number, number, number, number] | undefined>(undefined);

  // Helper to convert backend paths to frontend static paths
  const processFilePaths = (paths: string[]): string[] => {
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
    return staticPaths;
  };

  const fetchSessions = async () => {
    try {
      const res = await fetch('http://localhost:8001/api/sessions');
      if (res.ok) {
        const data = await res.json();
        setSessions(data);
      }
    } catch (e) {
      console.error("Failed to fetch sessions", e);
    }
  };

  useEffect(() => {
    fetchSessions();
  }, [session]); // Refresh list when current session changes (e.g. title updated)

  // Poll for status
  useEffect(() => {
    if (!session) return;

    const checkStatus = async () => {
      try {
        const res = await fetch(`http://localhost:8001/api/session/${session.id}`);
        if (res.ok) {
          const data = await res.json();
          if (data.file_paths_json) {
            try {
              const paths = JSON.parse(data.file_paths_json);
              data.file_paths = processFilePaths(paths);

              if (data.file_paths.length > 0) {
                // Use the first file as default file_path for compatibility
                data.file_path = data.file_paths[0];
              }
            } catch (e) {
              // ignore parse error
            }
          }
          setSession(data);

          // If no current file selected, select the first one
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
      if (session) {
        // Upload to existing session
        const res = await fetch(`http://localhost:8001/api/session/${session.id}/upload`, {
          method: 'POST',
          body: formData
        });
        if (!res.ok) throw new Error('Upload failed');
        // The polling will pick up the new file list shortly
        alert("文件添加成功");
      } else {
        // Create new session
        const res = await fetch('http://localhost:8001/api/upload', {
          method: 'POST',
          body: formData
        });
        if (!res.ok) throw new Error('Upload failed');
        const data = await res.json();

        const staticPath = `/static/${file.name}`;

        // Initialize local state
        const newSession = {
          id: data.session_id,
          file_path: staticPath,
          file_paths: [staticPath],
          file_name: file.name,
          created_at: new Date().toISOString(),
          business_status: 'PENDING', mda_status: 'PENDING', financial_status: 'PENDING',
          competitor_status: 'PENDING', valuation_status: 'PENDING',
        } as AnalysisSession;

        setSession(newSession);
        setCurrentFile(staticPath);
        fetchSessions(); // Refresh list
      }
    } catch (err) {
      console.error(err);
      alert("上传失败，请检查后台连接。");
    }
  };

  const handleNewSession = () => {
    setSession(null);
    setCurrentFile(undefined);
    setCurrentStep('business');
  };

  const handleSessionSelect = (sess: AnalysisSession) => {
    // Create a shallow copy with computed file_paths from json to avoid immediate rendering issues before poll
    let processedPaths: string[] = [];
    if (sess.file_paths) {
      // If already processed (from list_sessions? backend usually returns clean obj but file_paths property is property getter in pydantic model, wait.)
      // The list_sessions returns pydantic objects. The serializer should include computed properties?
      // FastAPI usually serializes fields. AnalysisSession has file_paths property but Field excluded? 
      // SQLModel fields are include. The property `file_paths` needs `json.loads`... 
      // Actually the backend endpoint returns JSON where `file_paths` is computed if I used `response_model` property?
      // In `list_sessions`, it returns `AnalysisSession` objects. 
      // Let's assume on selection we set it, and the polling useEffect will fetch full details including paths.
    }

    setSession(sess);
    setCurrentStep('business');
    // File paths will be handled by the effect once session is set
    setCurrentFile(undefined);
  };

  const handleBackToList = () => {
    setSession(null);
    setCurrentFile(undefined);
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

  if (!session) {
    return (
      <main className={styles.container}>
        <SessionList
          sessions={sessions}
          onSelect={handleSessionSelect}
          onUpload={handleFileUpload}
        />
      </main>
    );
  }

  const handleFileDelete = async (fileKey: string) => {
    if (!session) return;
    if (!confirm("确定要删除这个文件吗？")) return;

    // fileKey is like '/static/filename.pdf'
    // Extract filename
    const parts = fileKey.split('/');
    const filename = parts[parts.length - 1];

    try {
      const res = await fetch(`http://localhost:8001/api/session/${session.id}/file?filename=${filename}`, {
        method: 'DELETE'
      });

      if (!res.ok) {
        throw new Error('Deletion failed');
      }

      const data = await res.json();

      // Update local session state
      // We can either refetch or update manually. Let's force a refetch/poll will pick it up.
      // But to be responsive, let's update local list if possible or just alert.
      // The polling `checkStatus` will likely overwrite our manual update if we don't handle it carefully.
      // Ideally wait for polling or just trigger a fetch.

      // Since polling runs every 3s, let's just wait or force a checkStatus call if we could.
      // We can also optimistically update the session object.

      if (data.file_paths) {
        // Backend returns absolute paths, we need to process them again if we want to update local immediately
        // Or just wait for the next poll cycle which is simpler.
      }

      // If the deleted file was the current viewing file, clear it
      if (currentFile === fileKey) {
        setCurrentFile(undefined);
      }

      alert("文件删除成功");

    } catch (err) {
      console.error(err);
      alert("删除失败");
    }
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

        onUploadFile={handleFileUpload}
        onDeleteFile={handleFileDelete}
        onBack={handleBackToList}
      />

      <div className={styles.mainContent}>
        <div className={styles.splitPane}>
          {/* Left: Analysis */}
          <div className={styles.leftPanel}>
            <div className={styles.panelHeader}>
              <h2 className={styles.panelTitle}>{stepTitles[currentStep]}</h2>
              <div>
                {!session ? (
                  <div className="text-gray-500 text-sm">请在左侧上传文档开始分析</div>
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
