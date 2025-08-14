const fs = require("fs");
const path = require("path");
const { spawn } = require("child_process");

class GeminiService {
  constructor() {
    this.pythonPath = "python"; // atau 'python3' di Linux/Mac
    this.ragSelectorPath = path.join(__dirname, "../gemini API/api_bridge.py");
  }

  // Call Native RAG System
  async callNativeRAG(question, userId = null) {
    return new Promise((resolve, reject) => {
      const process = spawn(this.pythonPath, [
        this.ragSelectorPath,
        "--mode",
        "native",
        "--question",
        question,
        "--user-id",
        userId || "anonymous",
        "--format",
        "json",
      ]);

      let output = "";
      let error = "";

      process.stdout.on("data", (data) => {
        output += data.toString();
      });

      process.stderr.on("data", (data) => {
        error += data.toString();
      });

      process.on("close", (code) => {
        if (code === 0) {
          try {
            const result = JSON.parse(output.trim());
            resolve({
              answer: result.answer,
              system: "native",
              accuracy: 96.8,
              responseTime: result.response_time || 0,
              sources: result.sources || [],
              geminiModel: "gemini-2.5-flash",
            });
          } catch (parseError) {
            resolve({
              answer: output.trim(),
              system: "native",
              accuracy: 96.8,
              responseTime: 0,
              sources: [],
              geminiModel: "gemini-2.5-flash",
            });
          }
        } else {
          reject(new Error(`Python process failed: ${error}`));
        }
      });

      setTimeout(() => {
        process.kill();
        reject(new Error("Request timeout"));
      }, 30000);
    });
  }

  // Call LangChain RAG System
  async callLangChainRAG(question, userId = null) {
    return new Promise((resolve, reject) => {
      const process = spawn(this.pythonPath, [
        this.ragSelectorPath,
        "--mode",
        "langchain",
        "--question",
        question,
        "--user-id",
        userId || "anonymous",
        "--format",
        "json",
      ]);

      let output = "";
      let error = "";

      process.stdout.on("data", (data) => {
        output += data.toString();
      });

      process.stderr.on("data", (data) => {
        error += data.toString();
      });

      process.on("close", (code) => {
        if (code === 0) {
          try {
            const result = JSON.parse(output.trim());
            resolve({
              answer: result.answer,
              system: "langchain",
              accuracy: 63.6,
              responseTime: result.response_time || 0,
              sources: result.sources || [],
              geminiModel: "gemini-1.5-flash",
            });
          } catch (parseError) {
            resolve({
              answer: output.trim(),
              system: "langchain",
              accuracy: 63.6,
              responseTime: 0,
              sources: [],
              geminiModel: "gemini-1.5-flash",
            });
          }
        } else {
          reject(new Error(`LangChain process failed: ${error}`));
        }
      });

      setTimeout(() => {
        process.kill();
        reject(new Error("Request timeout"));
      }, 30000);
    });
  }

  // Auto select best RAG system
  async autoSelectRAG(question, userId = null) {
    const legalKeywords = [
      "pasal",
      "undang",
      "konstitusi",
      "hukum",
      "peraturan",
      "UUD",
      "ayat",
    ];

    const isLegalQuestion = legalKeywords.some((keyword) =>
      question.toLowerCase().includes(keyword.toLowerCase())
    );

    if (isLegalQuestion) {
      return await this.callNativeRAG(question, userId);
    } else {
      return await this.callLangChainRAG(question, userId);
    }
  }

  // Compare both RAG systems
  async compareRAGSystems(question, userId = null) {
    try {
      const [nativeResult, langchainResult] = await Promise.all([
        this.callNativeRAG(question, userId),
        this.callLangChainRAG(question, userId),
      ]);

      return {
        question,
        native: nativeResult,
        langchain: langchainResult,
        recommendation:
          nativeResult.accuracy > langchainResult.accuracy
            ? "native"
            : "langchain",
      };
    } catch (error) {
      throw new Error(`Comparison failed: ${error.message}`);
    }
  }
}

module.exports = new GeminiService();
