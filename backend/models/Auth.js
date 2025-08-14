const mongoose = require('mongoose');

const chatMessageSchema = new mongoose.Schema({
    question: {
        type: String,
        required: true
    },
    answer: {
        type: String,
        required: true
    },
    ragSystem: {
        type: String,
        enum: ['native', 'langchain'],
        required: true
    },
    accuracy: {
        type: Number,
        min: 0,
        max: 100
    },
    responseTime: {
        type: Number
    },
    sources: [{
        type: String
    }],
    geminiModel: {
        type: String,
        default: 'gemini-2.5-flash'
    },
    userRating: {
        type: Number,
        min: 1,
        max: 5
    }
}, {
    timestamps: true
});

const chatRoomSchema = new mongoose.Schema({
    roomId: {
        type: String,
        required: true
    },
    title: {
        type: String,
        required: true
    },
    messages: [chatMessageSchema],
    isActive: {
        type: Boolean,
        default: true
    },
    lastActivity: {
        type: Date,
        default: Date.now
    }
}, {
    timestamps: true
});

const userSchema = new mongoose.Schema({
    name: {
        type: String,
        required: [true, 'Please provide a name'],
        trim: true,
        maxlength: [50, 'Name cannot exceed 50 characters']
    },
    email: {
        type: String,
        required: [true, 'Please provide an email'],
        unique: true,
        lowercase: true,
        match: [
            /^\w+([.-]?\w+)*@\w+([.-]?\w+)*(\.\w{2,3})+$/,
            'Please provide a valid email'
        ]
    },
    password: {
        type: String,
        required: [true, 'Please provide a password'],
        minlength: [6, 'Password must be at least 6 characters'],
        select: false
    },
    role: {
        type: String,
        enum: ['user', 'admin', 'moderator'],
        default: 'user'
    },
    
    // Chat Rooms untuk User
    chatRooms: [chatRoomSchema],
    
    // User Preferences untuk RAG
    ragPreferences: {
        defaultSystem: {
            type: String,
            enum: ['native', 'langchain'],
            default: 'native'
        },
        saveHistory: {
            type: Boolean,
            default: true
        },
        maxRoomsLimit: {
            type: Number,
            default: 10
        }
    },
    
    lastLogin: {
        type: Date,
        default: Date.now
    },
    isActive: {
        type: Boolean,
        default: true
    }
}, {
    timestamps: true
});

// Index untuk performance
userSchema.index({ email: 1 });
userSchema.index({ 'chatRooms.roomId': 1 });
userSchema.index({ 'chatRooms.lastActivity': -1 });

module.exports = mongoose.model('User', userSchema);