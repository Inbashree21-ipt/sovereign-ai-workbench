import React, {
  useState,
  useEffect,
  useRef
} from 'react';

import {
  Send,
  Paperclip,
  Image as ImageIcon,
  Trash2,
  Bot,
  ShieldCheck,
  FileCheck,
  X
} from 'lucide-react';

import { ModelSelector } from '../components/chat/ModelSelector';
import { ChatMessage } from '../components/chat/ChatMessage';

import {
  sendChatMessage,
  analyzeImage,
  getModels
} from '../services/api';


export const ChatPage = () => {

  /* =====================================================
     CHAT MESSAGES
     ===================================================== */

  const [messages, setMessages] = useState([
    {
      id: 'msg-1',

      sender: 'ai',

      model: 'qwen2.5-coder:3b',

      text:
        'Greetings. I am your Sovereign On-Premise AI Workbench assistant. All calculations, vector queries, and document parsing are performed locally on your air-gapped machine. How can I assist with your industrial operations today?',

      timestamp: '09:00 AM',

      citations: [],

      reasoningSteps: [
        'System booted in air-gapped security mode',
        'Verified local qwen2.5-coder:3b weights loaded'
      ]
    }
  ]);


  /* =====================================================
     STATE
     ===================================================== */

  const [inputPrompt, setInputPrompt] =
    useState('');

  const [selectedModel, setSelectedModel] =
    useState('qwen2.5-coder:3b');

  const [models, setModels] =
    useState([]);

  const [isSending, setIsSending] =
    useState(false);

  const [attachedFiles, setAttachedFiles] =
    useState([]);

  const chatEndRef =
    useRef(null);


  /* =====================================================
     LOAD LOCAL MODELS
     ===================================================== */

  useEffect(() => {

    const loadModels = async () => {

      try {

        const data =
          await getModels();

        setModels(data);

      } catch (error) {

        console.error(
          'Failed to load models:',
          error
        );

      }

    };

    loadModels();

  }, []);


  /* =====================================================
     AUTO SCROLL
     ===================================================== */

  useEffect(() => {

    chatEndRef.current?.scrollIntoView({
      behavior: 'smooth'
    });

  }, [messages]);


  /* =====================================================
     SEND MESSAGE
     ===================================================== */

  const handleSend = async (e) => {

    if (e) {
      e.preventDefault();
    }


    if (
      (
        !inputPrompt.trim() &&
        attachedFiles.length === 0
      ) ||
      isSending
    ) {

      return;

    }


    const currentText =
      inputPrompt.trim();

    const currentFiles =
      [...attachedFiles];


    /* ===================================================
       USER MESSAGE
       =================================================== */

    const userMessage = {

      id:
        `user-${Date.now()}`,

      sender:
        'user',

      text:
        currentText +
        (
          currentFiles.length > 0
            ? `\n[Attached: ${currentFiles
                .map(
                  (file) =>
                    file.name
                )
                .join(', ')}]`
            : ''
        ),

      timestamp:
        new Date().toLocaleTimeString(
          [],
          {
            hour: '2-digit',
            minute: '2-digit'
          }
        )

    };


    setMessages((prev) => [
      ...prev,
      userMessage
    ]);


    /* ===================================================
       CLEAR INPUT
       =================================================== */

    setInputPrompt('');

    setAttachedFiles([]);

    setIsSending(true);


    try {

      /* =================================================
         IMAGE REQUEST
         ================================================= */

      const imageFile =
        currentFiles.find(
          (file) =>
            file.type &&
            file.type.startsWith(
              'image/'
            )
        );


      if (imageFile) {

        /*
         * If an image is attached,
         * send it to the real /vision endpoint.
         *
         * Backend:
         * FastAPI -> Ollama -> gemma3:4b
         */

        const visionPrompt =
          currentText ||
          'Describe this image in detail and identify any important technical information visible in it.';


        const aiReply =
          await analyzeImage(
            imageFile,
            visionPrompt
          );


        setMessages((prev) => [
          ...prev,
          aiReply
        ]);


        return;

      }


      /* =================================================
         NORMAL TEXT CHAT
         ================================================= */

      const aiReply =
        await sendChatMessage(
          currentText,
          selectedModel,
          currentFiles
        );


      setMessages((prev) => [
        ...prev,
        aiReply
      ]);

    } catch (err) {

      console.error(
        'Chat error:',
        err
      );


      setMessages((prev) => [

        ...prev,

        {
          id:
            `error-${Date.now()}`,

          sender:
            'ai',

          model:
            selectedModel,

          text:
            `Unable to process the request.\n\n${
              err?.message ||
              'Please check that the local FastAPI backend and Ollama are running.'
            }`,

          timestamp:
            new Date().toLocaleTimeString(
              [],
              {
                hour: '2-digit',
                minute: '2-digit'
              }
            ),

          citations: [],

          reasoningSteps: [
            'Local backend request failed'
          ]

        }

      ]);

    } finally {

      setIsSending(false);

    }

  };


  /* =====================================================
     ATTACH DOCUMENT
     ===================================================== */

  const handleAttachDocument = () => {

    const input =
      document.createElement(
        'input'
      );

    input.type =
      'file';

    input.accept =
      '.pdf,.docx,.txt';

    input.onchange =
      (e) => {

        if (
          e.target.files &&
          e.target.files[0]
        ) {

          setAttachedFiles(
            (prev) => [
              ...prev,
              e.target.files[0]
            ]
          );

        }

      };

    input.click();

  };


  /* =====================================================
     ATTACH IMAGE
     ===================================================== */

  const handleAttachImage = () => {

    const input =
      document.createElement(
        'input'
      );

    input.type =
      'file';

    input.accept =
      'image/*';

    input.onchange =
      (e) => {

        if (
          e.target.files &&
          e.target.files[0]
        ) {

          setAttachedFiles(
            (prev) => [
              ...prev,
              e.target.files[0]
            ]
          );

        }

      };

    input.click();

  };


  /* =====================================================
     REMOVE ATTACHMENT
     ===================================================== */

  const handleRemoveAttachment = (
    index
  ) => {

    setAttachedFiles(
      (prev) =>
        prev.filter(
          (_, i) =>
            i !== index
        )
    );

  };


  /* =====================================================
     CLEAR CHAT
     ===================================================== */

  const handleClearChat = () => {

    setMessages([
      {
        id:
          `msg-${Date.now()}`,

        sender:
          'ai',

        model:
          'qwen2.5-coder:3b',

        text:
          'Chat history cleared locally. Sovereign AI workspace ready for confidential queries.',

        timestamp:
          new Date().toLocaleTimeString(
            [],
            {
              hour: '2-digit',
              minute: '2-digit'
            }
          ),

        citations: [],

        reasoningSteps: [
          'Local message buffer flushed'
        ]

      }
    ]);

  };


  /* =====================================================
     RENDER
     ===================================================== */

  return (

    <div className="flex flex-col h-[calc(100vh-4rem)] bg-slate-950">


      {/* =================================================
          TOP CONTROLS BAR
          ================================================= */}

      <div className="px-6 py-3 bg-slate-900 border-b border-slate-800 flex items-center justify-between gap-4">

        <div className="flex items-center gap-4">

          <ModelSelector
            selectedModel={
              selectedModel
            }

            onSelectModel={
              setSelectedModel
            }

            models={
              models
            }
          />


          <div className="hidden md:flex items-center gap-2 text-xs text-emerald-400 bg-emerald-500/10 px-3 py-1 rounded-full border border-emerald-500/20">

            <ShieldCheck className="w-3.5 h-3.5" />

            <span>
              ChromaDB RAG Context Active
            </span>

          </div>

        </div>


        <button
          onClick={
            handleClearChat
          }

          className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-rose-500/10 hover:text-rose-400 text-slate-400 text-xs font-semibold flex items-center gap-1.5 transition-colors border border-slate-700"

          title="Clear local conversation history"
        >

          <Trash2 className="w-3.5 h-3.5" />

          <span>
            Clear Chat
          </span>

        </button>

      </div>


      {/* =================================================
          MESSAGE LIST
          ================================================= */}

      <div className="flex-1 p-6 overflow-y-auto space-y-4">

        {messages.map(
          (msg) => (

            <ChatMessage
              key={
                msg.id
              }

              message={
                msg
              }
            />

          )
        )}


        {/* ===============================================
            PROCESSING INDICATOR
            =============================================== */}

        {isSending && (

          <div className="flex items-center gap-3 p-4 rounded-xl bg-slate-900 border border-slate-800 text-cyan-400 text-xs font-mono animate-pulse">

            <Bot className="w-5 h-5 animate-spin text-cyan-400" />

            <span>

              Sovereign Model processing locally...

            </span>

          </div>

        )}


        <div
          ref={
            chatEndRef
          }
        />

      </div>


      {/* =================================================
          INPUT AREA
          ================================================= */}

      <div className="p-4 bg-slate-900 border-t border-slate-800">


        {/* ===============================================
            ATTACHED FILES
            =============================================== */}

        {attachedFiles.length > 0 && (

          <div className="mb-2 flex flex-wrap gap-2">

            {attachedFiles.map(
              (file, idx) => (

                <div
                  key={
                    `${file.name}-${idx}`
                  }

                  className="flex items-center gap-1.5 px-2.5 py-1 rounded bg-slate-950 text-cyan-300 border border-cyan-500/30 text-xs font-mono"
                >

                  {file.type?.startsWith(
                    'image/'
                  ) ? (

                    <ImageIcon className="w-3.5 h-3.5 text-cyan-400" />

                  ) : (

                    <FileCheck className="w-3.5 h-3.5 text-cyan-400" />

                  )}


                  <span>
                    {file.name}
                  </span>


                  <button
                    type="button"

                    onClick={() =>
                      handleRemoveAttachment(
                        idx
                      )
                    }

                    className="text-slate-400 hover:text-rose-400 ml-1"

                    title="Remove attachment"
                  >

                    <X className="w-3.5 h-3.5" />

                  </button>

                </div>

              )
            )}

          </div>

        )}


        {/* ===============================================
            INPUT FORM
            =============================================== */}

        <form
          onSubmit={
            handleSend
          }

          className="flex items-center gap-2"
        >


          {/* =============================================
              ACTION BUTTONS
              ============================================= */}

          <div className="flex items-center gap-1 bg-slate-950 p-1.5 rounded-xl border border-slate-800">


            {/* DOCUMENT */}

            <button
              type="button"

              onClick={
                handleAttachDocument
              }

              className="p-2 text-slate-400 hover:text-cyan-400 hover:bg-slate-800 rounded-lg transition-colors"

              title="Attach Confidential Document (PDF, DOCX, TXT)"
            >

              <Paperclip className="w-4 h-4" />

            </button>


            {/* IMAGE */}

            <button
              type="button"

              onClick={
                handleAttachImage
              }

              className="p-2 text-slate-400 hover:text-cyan-400 hover:bg-slate-800 rounded-lg transition-colors"

              title="Analyze image with local Gemma multimodal model"
            >

              <ImageIcon className="w-4 h-4" />

            </button>

          </div>


          {/* =============================================
              PROMPT
              ============================================= */}

          <input

            type="text"

            value={
              inputPrompt
            }

            onChange={
              (e) =>
                setInputPrompt(
                  e.target.value
                )
            }

            placeholder="Ask Sovereign AI about refinery SOPs, safety compliance, code generation, or attach an image..."

            className="flex-1 bg-slate-950 text-slate-100 text-sm rounded-xl px-4 py-3 border border-slate-800 focus:outline-none focus:border-cyan-500 transition-colors placeholder:text-slate-500 shadow-inner"

          />


          {/* =============================================
              SEND
              ============================================= */}

          <button

            type="submit"

            disabled={
              (
                !inputPrompt.trim() &&
                attachedFiles.length === 0
              ) ||
              isSending
            }

            className="px-5 py-3 rounded-xl bg-gradient-to-r from-cyan-500 to-emerald-500 hover:from-cyan-400 hover:to-emerald-400 disabled:opacity-50 text-slate-950 font-bold text-sm flex items-center gap-2 transition-all shadow-md shadow-cyan-500/10 cursor-pointer"

          >

            <span>
              Send
            </span>

            <Send className="w-4 h-4" />

          </button>

        </form>


        {/* ===============================================
            SECURITY FOOTER
            =============================================== */}

        <p className="text-[10px] text-center text-slate-500 mt-2 font-mono">

          Air-gapped execution mode active. Inputs are processed strictly on local GPU/CPU memory.

        </p>

      </div>

    </div>

  );

};