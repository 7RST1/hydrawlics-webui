
export type FileStatus = {
  // iso date string, e.g. "2025-09-12T02:01:53.776503"
  completed_at: string,
  // iso date string, e.g. "2025-09-12T02:01:42.776178"
  created_at: string,
  // e.g. "/jobs/accfdfd6-1404-43fb-b518-e2de412c9cad/download"
  download_url?: string,
  job_id: string,
  progress: number,
  status: 'queued' | 'processing' | 'completed' | 'failed'
}