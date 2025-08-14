const express = require("express");

const {
  createChatRoom,
  getChatRooms,
  getChatRoomMessages,
  deleteChatRoom,
  processChatQuestion,
} = require("../controllers/chatController");
const { protect } = require("../middleware/auth");

const router = express.Router();

// All routes are protected
router.use(protect);

// Chat room management
router.post("/rooms", createChatRoom);
router.get("/rooms", getChatRooms);
router.get("/rooms/:roomId/messages", getChatRoomMessages);
router.delete("/rooms/:roomId", deleteChatRoom);

// RAG processing
router.post("/ask", processChatQuestion);

module.exports = router;
