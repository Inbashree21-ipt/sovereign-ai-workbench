/**
 * API SERVICE LAYER
 * Sovereign On-Premise Agentic AI Workbench
 *
 * Backend:
 * FastAPI + Ollama
 *
 * Local backend URL:
 * http://127.0.0.1:8000
 */


/* =========================================================
   LOCAL CONFIGURATION
   ========================================================= */

const BACKEND_URL = 'http://127.0.0.1:8000';


/* =========================================================
   MOCK DOCUMENT STORAGE
   ========================================================= */

let documentsStore = [
  {
    id: 'doc-1',
    name: 'Safety_SOP_2025.pdf',
    category: 'Safety & SOP',
    type: 'PDF',
    size: '4.2 MB',
    uploadDate: '2026-09-01',
    status: 'Indexed',
    chunksCount: 142,
    confidence: '99.4%'
  },
  {
    id: 'doc-2',
    name: 'Inspection_Report_Turbine_A.pdf',
    category: 'Inspection Log',
    type: 'PDF',
    size: '8.7 MB',
    uploadDate: '2026-09-04',
    status: 'Indexed',
    chunksCount: 288,
    confidence: '98.9%'
  },
  {
    id: 'doc-3',
    name: 'Maintenance_Manual_Refinery_V3.pdf',
    category: 'Maintenance',
    type: 'Maintenance',
    size: '18.1 MB',
    uploadDate: '2026-09-06',
    status: 'Indexed',
    chunksCount: 512,
    confidence: '99.8%'
  },
  {
    id: 'doc-4',
    name: 'Environmental_Compliance_Audit.docx',
    category: 'Audit',
    type: 'DOCX',
    size: '2.9 MB',
    uploadDate: '2026-09-07',
    status: 'Processing',
    chunksCount: 64,
    confidence: '95.0%'
  }
];


/* =========================================================
   SYSTEM TELEMETRY API
   ========================================================= */

export const getSystemStatus = async () => {
  try {
    const response = await fetch(
      `${BACKEND_URL}/models`
    );

    if (!response.ok) {
      throw new Error(
        `Backend error: ${response.status}`
      );
    }

    const data = await response.json();

    const models = data.models || [];

    const primaryModel =
      models.find((model) =>
        model.name
          .toLowerCase()
          .includes('qwen2.5-coder')
      ) || models[0];

    return {
      environment: 'LOCAL / ON-PREMISE',

      localServerUrl: BACKEND_URL,

      activeModel:
        primaryModel?.name ||
        'No local model available',

      availableModelsCount:
        models.length,

      totalDocuments:
        documentsStore.length,

      networkStatus:
        'Local Backend',

      externalCallsCount:
        'Not tracked',

      securityStatus:
        'Local Runtime',

      cloudApiDisabled:
        true
    };

  } catch (error) {

    console.error(
      'Failed to load system status:',
      error
    );

    return {
      environment:
        'LOCAL / ON-PREMISE',

      localServerUrl:
        BACKEND_URL,

      activeModel:
        'Unavailable',

      availableModelsCount:
        0,

      totalDocuments:
        documentsStore.length,

      networkStatus:
        'Backend Unavailable',

      externalCallsCount:
        'Not tracked',

      securityStatus:
        'Local Runtime',

      cloudApiDisabled:
        true
    };
  }
};


/* =========================================================
   AI CHAT API
   ========================================================= */

export const sendChatMessage = async (
  userPrompt,
  modelId = null,
  attachments = []
) => {

  /*
   * Normal text chat uses /ask.
   *
   * The backend router automatically selects:
   *
   * Coding  -> qwen2.5-coder:3b
   * General -> llama3.2:3b
   * Vision  -> gemma3:4b
   */

  const response = await fetch(
    `${BACKEND_URL}/ask`,
    {
      method: 'POST',

      headers: {
        'Content-Type': 'application/json',
      },

      body: JSON.stringify({
        prompt: userPrompt,
      }),
    }
  );

  if (!response.ok) {

    throw new Error(
      `Backend error: ${response.status}`
    );

  }

  const data =
    await response.json();

  return {

    id:
      `msg-${Date.now()}`,

    sender:
      'ai',

    model:
      data.model,

    text:
      data.response,

    timestamp:
      new Date().toLocaleTimeString(
        [],
        {
          hour: '2-digit',
          minute: '2-digit',
        }
      ),

    citations: [],

    reasoningSteps: [

      `Task routed as: ${data.task}`,

      `Local model used: ${data.model}`,

    ],

  };
};


/* =========================================================
   VISION / IMAGE ANALYSIS API
   ========================================================= */

export const analyzeImage = async (
  imageFile,
  prompt = 'Describe this image in detail.'
) => {

  if (!imageFile) {

    throw new Error(
      'No image file was provided.'
    );

  }

  /*
   * FastAPI /vision expects:
   *
   * prompt -> text
   * image  -> uploaded image file
   */

  const formData =
    new FormData();

  formData.append(
    'prompt',
    prompt
  );

  formData.append(
    'image',
    imageFile
  );

  const response =
    await fetch(
      `${BACKEND_URL}/vision`,
      {
        method: 'POST',

        body: formData,
      }
    );

  if (!response.ok) {

    let errorMessage =
      `Vision backend error: ${response.status}`;

    try {

      const errorData =
        await response.json();

      if (errorData.detail) {
        errorMessage =
          errorData.detail;
      }

    } catch {
      // Keep default error message.
    }

    throw new Error(
      errorMessage
    );

  }

  const data =
    await response.json();

  return {

    id:
      `vision-${Date.now()}`,

    sender:
      'ai',

    model:
      data.model ||
      'gemma3:4b',

    text:
      data.response ||
      'No image analysis response received.',

    filename:
      data.filename ||
      imageFile.name,

    timestamp:
      new Date().toLocaleTimeString(
        [],
        {
          hour: '2-digit',
          minute: '2-digit',
        }
      ),

    citations: [],

    reasoningSteps: [

      'Task routed as: vision',

      `Local model used: ${
        data.model || 'gemma3:4b'
      }`,

      'Image processed by local Ollama runtime',

    ],

  };

};


/* =========================================================
   DOCUMENTS API
   ========================================================= */

export const getDocuments = async () => {

  return [
    ...documentsStore
  ];

};


export const uploadDocument = async (
  fileObj
) => {

  await new Promise(
    resolve =>
      setTimeout(
        resolve,
        600
      )
  );

  const newDoc = {

    id:
      `doc-${Date.now()}`,

    name:
      fileObj.name ||
      'Uploaded_Document.pdf',

    category:
      'User Upload',

    type:
      fileObj.name
        ? fileObj.name
            .split('.')
            .pop()
            .toUpperCase()
        : 'PDF',

    size:
      fileObj.size
        ? `${(
            fileObj.size /
            (1024 * 1024)
          ).toFixed(1)} MB`
        : '3.5 MB',

    uploadDate:
      new Date()
        .toISOString()
        .split('T')[0],

    status:
      'Indexed',

    chunksCount:
      Math.floor(
        Math.random() * 150
      ) + 20,

    confidence:
      '99.1%'

  };

  documentsStore.unshift(
    newDoc
  );

  return newDoc;

};


export const deleteDocument = async (
  id
) => {

  documentsStore =
    documentsStore.filter(
      d =>
        d.id !== id
    );

  return {

    success:
      true,

    id

  };

};


/* =========================================================
   KNOWLEDGE BASE / RAG API
   ========================================================= */

export const searchKnowledgeBase = async (
  query
) => {

  await new Promise(
    resolve =>
      setTimeout(
        resolve,
        400
      )
  );

  const mockChunks = [

    {
      id:
        'chk-101',

      docName:
        'Safety_SOP_2025.pdf',

      page:
        14,

      similarity:
        '98.7%',

      chunkText:
        `SECTION 4.2 - AIR-GAPPED CONTROL ROOM OPERATING PROCEDURES: All high-pressure steam valves (V-102 through V-118) must be physically tagged and logged prior to scheduled maintenance shutdowns. Local PLC telemetry is mirrored every 300 seconds.`

    },

    {
      id:
        'chk-102',

      docName:
        'Inspection_Report_Turbine_A.pdf',

      page:
        8,

      similarity:
        '94.2%',

      chunkText:
        `PARAGRAPH 3.1 - TURBINE BLADE WEAR ASSESSMENT: Vibration analysis indicated a frequency anomaly at 120 Hz during full-load testing. Recommended rotor balancing during upcoming Q4 turnaround.`

    },

    {
      id:
        'chk-103',

      docName:
        'Maintenance_Manual_Refinery_V3.pdf',

      page:
        142,

      similarity:
        '89.5%',

      chunkText:
        `APPENDIX B - RECTIFIER OVERHAUL SPECIFICATIONS: Replace main silicon diodes if reverse leakage current exceeds 15mA at peak reverse voltage. Use only certified OEM replacement kits.`

    }

  ];

  if (
    !query ||
    query.trim() === ''
  ) {

    return mockChunks;

  }

  return mockChunks.filter(
    c =>

      c.chunkText
        .toLowerCase()
        .includes(
          query.toLowerCase()
        )

      ||

      c.docName
        .toLowerCase()
        .includes(
          query.toLowerCase()
        )
  );

};


/* =========================================================
   AGENT TASKS API
   ========================================================= */

export const getAgentTasks = async () => {

  return [];

};


export const createAgentTask = async (
  taskData
) => {

  const response = await fetch(
    `${BACKEND_URL}/agent`,
    {
      method: 'POST',

      headers: {
        'Content-Type':
          'application/json',
      },

      body: JSON.stringify({

        prompt:
          `${taskData.title}. Source document: ${taskData.sourceDocument}. Output format: ${taskData.outputFormat}.`

      }),

    }
  );

  if (!response.ok) {

    throw new Error(
      `Backend error: ${response.status}`
    );

  }

  const data =
    await response.json();

  return {

    id:
      `task-${Date.now()}`,

    title:
      taskData.title,

    sourceDocument:
      taskData.sourceDocument ||
      'None',

    outputFormat:
      taskData.outputFormat ||
      'AI Generated',

    currentStage:
      data.success
        ? 'Completed'
        : 'Failed',

    stageIndex:
      data.success
        ? 5
        : 0,

    progress:
      data.success
        ? 100
        : 0,

    status:
      data.success
        ? 'Completed'
        : 'Failed',

    createdAt:
      new Date()
        .toISOString()
        .replace(
          'T',
          ' '
        )
        .substring(
          0,
          16
        ),

    toolCalls: [

      {

        name:
          'ReAct Agent',

        timestamp:
          new Date()
            .toLocaleTimeString(),

        status:
          data.success
            ? 'Success'
            : 'Failed',

        result:
          data.response,

      }

    ],

    outputFile:
      data.deliverables?.[0] ||
      null,

    response:
      data.response,

    model:
      data.model,

    task:
      data.task,

    steps:
      data.steps,

  };

};


/* =========================================================
   MODELS API
   ========================================================= */

export const getModels = async () => {

  const response =
    await fetch(
      `${BACKEND_URL}/models`
    );

  if (!response.ok) {

    throw new Error(
      `Backend error: ${response.status}`
    );

  }

  const data =
    await response.json();

  return data.models || [];

};


/*
 * Model status control is currently not connected
 * to Ollama.
 *
 * Models are managed by the local
 * Ollama runtime.
 */

export const toggleModelStatus = async (
  modelId
) => {

  console.warn(
    'Model status control is not connected to Ollama:',
    modelId
  );

  return await getModels();

};


/* =========================================================
   GENERATED FILES API
   ========================================================= */

export const getGeneratedFiles = async () => {

  const response =
    await fetch(
      `${BACKEND_URL}/deliverables`
    );

  if (!response.ok) {

    throw new Error(
      `Backend error: ${response.status}`
    );

  }

  const data =
    await response.json();

  return data.files || [];

};


/*
 * File deletion is not currently exposed
 * by the FastAPI backend.
 */

export const deleteGeneratedFile = async (
  id
) => {

  console.warn(
    'Generated file deletion is not connected to the backend:',
    id
  );

  return {

    success:
      false,

    id,

    message:
      'File deletion is not currently implemented.'

  };

};


/* =========================================================
   DOWNLOAD GENERATED FILE
   ========================================================= */

export const getDeliverableDownloadUrl = (
  filename
) => {

  if (!filename) {
    return null;
  }

  return (
    `${BACKEND_URL}/deliverables/download/` +
    `${encodeURIComponent(filename)}`
  );

};


/* =========================================================
   EXPORT BACKEND URL
   ========================================================= */

export {
  BACKEND_URL
};