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
   SYSTEM TELEMETRY API
   ========================================================= */

export const getSystemStatus = async () => {

  try {

    const [modelsResponse, ragResponse] =
      await Promise.all([
        fetch(`${BACKEND_URL}/models`),
        fetch(`${BACKEND_URL}/rag/status`)
      ]);


    if (!modelsResponse.ok) {

      throw new Error(
        `Models backend error: ${modelsResponse.status}`
      );

    }


    if (!ragResponse.ok) {

      throw new Error(
        `RAG backend error: ${ragResponse.status}`
      );

    }


    const modelsData =
      await modelsResponse.json();

    const ragData =
      await ragResponse.json();


    const models =
      modelsData.models || [];


    const primaryModel =
      models.find((model) =>
        model.name
          .toLowerCase()
          .includes('qwen2.5-coder')
      ) || models[0];


    return {

      environment:
        'LOCAL / ON-PREMISE',

      localServerUrl:
        BACKEND_URL,

      activeModel:
        primaryModel?.name ||
        'No local model available',

      availableModelsCount:
        models.length,

      totalDocuments:
        ragData.totalDocuments || 0,

      indexedChunksTotal:
        ragData.indexedChunksTotal || 0,

      vectorStore:
        ragData.vectorStore || 'FAISS',

      embeddingModel:
        ragData.embeddingModel ||
        'sentence-transformers/all-MiniLM-L6-v2',

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
        0,

      indexedChunksTotal:
        0,

      vectorStore:
        'FAISS',

      embeddingModel:
        'sentence-transformers/all-MiniLM-L6-v2',

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

/*
 * Documents are now managed by the real
 * Member 3 FastAPI RAG backend.
 *
 * Backend endpoints:
 *
 * GET    /rag/documents
 * POST   /rag/upload
 * DELETE /rag/documents/{filename}
 */


/* ---------------------------------------------------------
   Get Documents
   --------------------------------------------------------- */

export const getDocuments = async () => {

  const response =
    await fetch(
      `${BACKEND_URL}/rag/documents`
    );


  if (!response.ok) {

    throw new Error(
      `Documents backend error: ${response.status}`
    );

  }


  const data =
    await response.json();


  return data.documents || [];

};


/* ---------------------------------------------------------
   Upload Document
   --------------------------------------------------------- */

export const uploadDocument = async (
  fileObj
) => {

  if (!fileObj) {

    throw new Error(
      'No document file was provided.'
    );

  }


  const formData =
    new FormData();


  formData.append(
    'file',
    fileObj
  );


  const response =
    await fetch(
      `${BACKEND_URL}/rag/upload`,
      {

        method: 'POST',

        body: formData,

      }
    );


  if (!response.ok) {

    let errorMessage =
      `Document upload error: ${response.status}`;


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


  return data.document || data;

};


/* ---------------------------------------------------------
   Delete Document
   --------------------------------------------------------- */

export const deleteDocument = async (
  id
) => {

  if (!id) {

    throw new Error(
      'Document filename is required.'
    );

  }


  const response =
    await fetch(
      `${BACKEND_URL}/rag/documents/${encodeURIComponent(id)}`,
      {
        method: 'DELETE',
      }
    );


  if (!response.ok) {

    let errorMessage =
      `Document deletion error: ${response.status}`;


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


  return await response.json();

};


/* =========================================================
   KNOWLEDGE BASE / RAG API
   ========================================================= */

export const searchKnowledgeBase = async (
  query
) => {

  if (
    !query ||
    query.trim() === ''
  ) {

    return [];

  }


  const response = await fetch(
    `${BACKEND_URL}/rag/search`,
    {

      method: 'POST',

      headers: {
        'Content-Type': 'application/json',
      },

      body: JSON.stringify({
        question: query,
      }),

    }
  );


  if (!response.ok) {

    throw new Error(
      `RAG search backend error: ${response.status}`
    );

  }


  const data =
    await response.json();


  return (
    data.results || []
  ).map((result) => ({

    id:
      result.id,

    docName:
      result.docName,

    page:
      result.page,

    distance:
      result.distance,

    chunkText:
      result.chunkText,

  }));

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

  const response =
    await fetch(
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