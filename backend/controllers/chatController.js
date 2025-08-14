const User = require("../models/Auth");
const { v4: uuidv4 } = require("uuid");

// @desc    Create new chat room
// @route   POST /api/chat/rooms
// @access  Private
exports.createChatRoom = async (req, res) => {
  try {
    const { title } = req.body;
    const userId = req.user.id;

    console.log("Creating chat room for user:", userId);

    const user = await User.findById(userId);
    if (!user) {
      return res.status(404).json({
        success: false,
        message: "User not found",
      });
    }

    // Initialize chatRooms array if not exists
    if (!user.chatRooms) {
      user.chatRooms = [];
    }

    // Initialize ragPreferences if not exists
    if (!user.ragPreferences) {
      user.ragPreferences = {
        defaultSystem: "native",
        saveHistory: true,
        maxRoomsLimit: 10,
      };
    }

    // Check room limit
    const activeRooms = user.chatRooms.filter((room) => room.isActive);
    if (activeRooms.length >= user.ragPreferences.maxRoomsLimit) {
      return res.status(400).json({
        success: false,
        message: `Maximum ${user.ragPreferences.maxRoomsLimit} active rooms allowed`,
      });
    }

    // Create new room
    const newRoom = {
      roomId: uuidv4(),
      title: title || `Chat Room ${Date.now()}`,
      messages: [],
      isActive: true,
      lastActivity: new Date(),
    };

    user.chatRooms.push(newRoom);
    await user.save();

    console.log("Chat room created successfully:", newRoom.roomId);

    res.status(201).json({
      success: true,
      message: "Chat room created successfully",
      data: {
        room: newRoom,
      },
    });
  } catch (error) {
    console.error("Create chat room error:", error);
    res.status(500).json({
      success: false,
      message: "Server error creating chat room",
      error: error.message,
    });
  }
};

// @desc    Get user's chat rooms
// @route   GET /api/chat/rooms
// @access  Private
exports.getChatRooms = async (req, res) => {
  try {
    const userId = req.user.id;
    const { limit = 10, active = true } = req.query;

    console.log("Getting chat rooms for user:", userId);

    const user = await User.findById(userId).select("chatRooms");
    if (!user) {
      return res.status(404).json({
        success: false,
        message: "User not found",
      });
    }

    // Initialize chatRooms if not exists
    let rooms = user.chatRooms || [];

    // Filter active rooms if requested
    if (active === "true") {
      rooms = rooms.filter((room) => room.isActive);
    }

    // Sort by last activity
    rooms.sort((a, b) => new Date(b.lastActivity) - new Date(a.lastActivity));

    // Limit results
    rooms = rooms.slice(0, parseInt(limit));

    // Add message count to each room
    const roomsWithStats = rooms.map((room) => ({
      ...room.toObject(),
      messageCount: room.messages ? room.messages.length : 0,
      lastMessage:
        room.messages && room.messages.length > 0
          ? room.messages[room.messages.length - 1]
          : null,
    }));

    res.status(200).json({
      success: true,
      data: {
        rooms: roomsWithStats,
        total: user.chatRooms ? user.chatRooms.length : 0,
      },
    });
  } catch (error) {
    console.error("Get chat rooms error:", error);
    res.status(500).json({
      success: false,
      message: "Server error getting chat rooms",
      error: error.message,
    });
  }
};

// @desc    Get chat room messages
// @route   GET /api/chat/rooms/:roomId/messages
// @access  Private
exports.getChatRoomMessages = async (req, res) => {
  try {
    const userId = req.user.id;
    const { roomId } = req.params;
    const { limit = 50, page = 1 } = req.query;

    console.log("Getting messages for room:", roomId);

    const user = await User.findById(userId);
    if (!user) {
      return res.status(404).json({
        success: false,
        message: "User not found",
      });
    }

    if (!user.chatRooms) {
      return res.status(404).json({
        success: false,
        message: "No chat rooms found",
      });
    }

    const room = user.chatRooms.find((room) => room.roomId === roomId);
    if (!room) {
      return res.status(404).json({
        success: false,
        message: "Chat room not found",
      });
    }

    // Pagination
    const startIndex = (page - 1) * limit;
    const endIndex = page * limit;

    const messages = room.messages || [];
    const sortedMessages = messages
      .sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt))
      .slice(startIndex, endIndex);

    res.status(200).json({
      success: true,
      data: {
        room: {
          roomId: room.roomId,
          title: room.title,
          isActive: room.isActive,
          lastActivity: room.lastActivity,
        },
        messages: sortedMessages,
        pagination: {
          current: parseInt(page),
          total: Math.ceil(messages.length / limit),
          hasNext: endIndex < messages.length,
          hasPrev: startIndex > 0,
        },
      },
    });
  } catch (error) {
    console.error("Get chat messages error:", error);
    res.status(500).json({
      success: false,
      message: "Server error getting chat messages",
      error: error.message,
    });
  }
};

// @desc    Process chat question with simulated RAG
// @route   POST /api/chat/ask
// @access  Private
exports.processChatQuestion = async (req, res) => {
  try {
    const userId = req.user.id;
    const { question, roomId, ragSystem = "auto" } = req.body;

    console.log("Processing question:", question, "for user:", userId);

    if (!question || !question.trim()) {
      return res.status(400).json({
        success: false,
        message: "Question is required",
      });
    }

    const startTime = Date.now();

    // Simulasi RAG response (untuk testing)
    let result;
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

    if (ragSystem === "native" || (ragSystem === "auto" && isLegalQuestion)) {
      result = {
        answer: `[Simulasi Native RAG] Jawaban untuk pertanyaan hukum: "${question}". 

Berdasarkan analisis menggunakan sistem Native RAG dengan Gemini 2.5 Flash, berikut adalah jawaban yang relevan:

Pertanyaan Anda berkaitan dengan aspek konstitusional Indonesia. Sistem kami menganalisis dokumen-dokumen hukum yang tersedia dalam database dan memberikan respons dengan akurasi tinggi.

Catatan: Ini adalah simulasi untuk testing. Dalam implementasi final, sistem akan terhubung dengan Gemini API dan database dokumen hukum yang sesungguhnya.`,
        system: "native",
        accuracy: 96.8,
        responseTime: 4200,
        sources: ["UUD1945.pdf", "Konstitusi_Indonesia.pdf"],
        geminiModel: "gemini-2.5-flash",
      };
    } else {
      result = {
        answer: `[Simulasi LangChain RAG] Jawaban untuk pertanyaan umum: "${question}". 

Menggunakan sistem LangChain RAG dengan Gemini 1.5 Flash, berikut adalah respons yang dihasilkan:

Sistem telah memproses pertanyaan Anda dan mencari informasi relevan dari database vektor. Jawaban ini dioptimalkan untuk kecepatan respons.

Catatan: Ini adalah simulasi untuk testing. Dalam implementasi final, sistem akan menggunakan LangChain framework dengan Gemini API.`,
        system: "langchain",
        accuracy: 63.6,
        responseTime: 2800,
        sources: ["VectorDB_General.txt"],
        geminiModel: "gemini-1.5-flash",
      };
    }

    const responseTime = Date.now() - startTime;

    // If roomId provided, save to chat history
    if (roomId) {
      const user = await User.findById(userId);
      if (user && user.chatRooms) {
        const roomIndex = user.chatRooms.findIndex(
          (room) => room.roomId === roomId
        );
        if (roomIndex !== -1) {
          const newMessage = {
            question: question.trim(),
            answer: result.answer,
            ragSystem: result.system,
            accuracy: result.accuracy,
            responseTime: result.responseTime || responseTime,
            sources: result.sources || [],
            geminiModel: result.geminiModel,
          };

          user.chatRooms[roomIndex].messages.push(newMessage);
          user.chatRooms[roomIndex].lastActivity = new Date();
          await user.save();

          console.log("Message saved to room:", roomId);
        }
      }
    }

    res.status(200).json({
      success: true,
      data: {
        question: question.trim(),
        answer: result.answer,
        system: result.system,
        accuracy: result.accuracy,
        responseTime: result.responseTime || responseTime,
        sources: result.sources || [],
        geminiModel: result.geminiModel,
        roomId: roomId || null,
        cached: false,
      },
    });
  } catch (error) {
    console.error("Process chat question error:", error);
    res.status(500).json({
      success: false,
      message: "Server error processing question",
      error: error.message,
    });
  }
};

// @desc    Delete chat room
// @route   DELETE /api/chat/rooms/:roomId
// @access  Private
exports.deleteChatRoom = async (req, res) => {
  try {
    const userId = req.user.id;
    const { roomId } = req.params;

    console.log("Deleting chat room:", roomId, "for user:", userId);

    const user = await User.findById(userId);
    if (!user) {
      return res.status(404).json({
        success: false,
        message: "User not found",
      });
    }

    if (!user.chatRooms) {
      return res.status(404).json({
        success: false,
        message: "No chat rooms found",
      });
    }

    const roomIndex = user.chatRooms.findIndex(
      (room) => room.roomId === roomId
    );
    if (roomIndex === -1) {
      return res.status(404).json({
        success: false,
        message: "Chat room not found",
      });
    }

    // Mark as inactive instead of deleting
    user.chatRooms[roomIndex].isActive = false;
    await user.save();

    console.log("Chat room deleted successfully:", roomId);

    res.status(200).json({
      success: true,
      message: "Chat room deleted successfully",
    });
  } catch (error) {
    console.error("Delete chat room error:", error);
    res.status(500).json({
      success: false,
      message: "Server error deleting chat room",
      error: error.message,
    });
  }
};
