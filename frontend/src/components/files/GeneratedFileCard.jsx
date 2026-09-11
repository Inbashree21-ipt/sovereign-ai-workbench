import React from 'react';
import {
  FileText,
  FileSpreadsheet,
  FileCode,
  Presentation,
  Download,
  Trash2,
  ShieldCheck
} from 'lucide-react';

import { Badge } from '../common/Badge';


export const GeneratedFileCard = ({
  file,
  onDelete,
  onDownload
}) => {

  // --------------------------------------------------
  // Determine file type from filename
  // --------------------------------------------------

  const getFileType = (filename) => {

    const extension = filename
      .split('.')
      .pop()
      .toLowerCase();

    switch (extension) {
      case 'pdf':
        return 'PDF';

      case 'docx':
        return 'DOCX';

      case 'xlsx':
        return 'XLSX';

      case 'pptx':
        return 'PPTX';

      case 'py':
        return 'PYTHON';

      default:
        return 'FILE';
    }
  };


  // --------------------------------------------------
  // File Icon
  // --------------------------------------------------

  const getFileIcon = (type) => {

    switch (type) {

      case 'PDF':
        return (
          <FileText className="w-6 h-6 text-rose-400" />
        );

      case 'DOCX':
        return (
          <FileText className="w-6 h-6 text-blue-400" />
        );

      case 'XLSX':
        return (
          <FileSpreadsheet className="w-6 h-6 text-emerald-400" />
        );

      case 'PPTX':
        return (
          <Presentation className="w-6 h-6 text-amber-400" />
        );

      case 'PYTHON':
        return (
          <FileCode className="w-6 h-6 text-cyan-400" />
        );

      default:
        return (
          <FileText className="w-6 h-6 text-slate-400" />
        );
    }
  };


  // --------------------------------------------------
  // Format File Size
  // --------------------------------------------------

  const formatFileSize = (bytes) => {

    if (!bytes) {
      return '0 B';
    }

    if (bytes < 1024) {
      return `${bytes} B`;
    }

    if (bytes < 1024 * 1024) {
      return `${(bytes / 1024).toFixed(1)} KB`;
    }

    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };


  // --------------------------------------------------
  // Format Created Date
  // --------------------------------------------------

  const formatCreatedDate = (timestamp) => {

    if (!timestamp) {
      return 'Unknown';
    }

    return new Date(timestamp * 1000).toLocaleString();
  };


  const fileType = getFileType(file.name);


  return (
    <div className="bg-slate-900 border border-slate-800 hover:border-cyan-500/30 rounded-xl p-5 shadow-lg transition-all duration-300 flex flex-col justify-between group">

      <div>

        {/* File Header */}

        <div className="flex items-start justify-between gap-3">

          <div className="flex items-center gap-3">

            <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 group-hover:border-slate-700 transition-colors">

              {getFileIcon(fileType)}

            </div>

            <div>

              <h4
                className="text-sm font-bold text-slate-100 font-mono truncate max-w-[180px]"
                title={file.name}
              >
                {file.name}
              </h4>

              <p className="text-xs text-slate-400">
                Generated Deliverable
              </p>

            </div>

          </div>


          <Badge
            variant="cyan"
            className="font-mono text-[10px]"
          >
            {fileType}
          </Badge>

        </div>


        {/* File Information */}

        <div className="mt-4 pt-3 border-t border-slate-800/80 space-y-1.5 text-xs text-slate-400 font-mono">

          <div className="flex justify-between">

            <span>Size:</span>

            <span className="text-slate-200">
              {formatFileSize(file.size)}
            </span>

          </div>


          <div className="flex justify-between">

            <span>Created:</span>

            <span className="text-slate-200">
              {formatCreatedDate(file.createdAt)}
            </span>

          </div>


          <div className="flex justify-between">

            <span>Storage:</span>

            <span className="text-cyan-400">
              Local
            </span>

          </div>

        </div>

      </div>


      {/* Actions */}

      <div className="mt-5 pt-3 border-t border-slate-800 flex items-center justify-between gap-2">

        <div className="flex items-center gap-1 text-[10px] text-emerald-400 font-semibold">

          <ShieldCheck className="w-3 h-3" />

          <span>Local File</span>

        </div>


        <div className="flex items-center gap-1.5">

          {/* Delete */}

          <button
            onClick={() => onDelete(file.name)}
            className="p-2 rounded-lg bg-slate-950 text-slate-400 hover:text-rose-400 hover:bg-rose-500/10 border border-slate-800 transition-colors"
            title="Delete file"
          >

            <Trash2 className="w-4 h-4" />

          </button>


          {/* Download */}

          <button
            onClick={() => onDownload(file.name)}
            className="px-3 py-2 rounded-lg bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold text-xs flex items-center gap-1.5 transition-colors shadow-md shadow-cyan-500/10"
          >

            <Download className="w-3.5 h-3.5" />

            <span>Download</span>

          </button>

        </div>

      </div>

    </div>
  );
};