"use client";

import { FormEvent, useState } from "react";

type Message = {
  role: "bot" | "user";
  text: string;
};

function answerQuestion(question: string) {
  const q = question.toLowerCase();

  if (q.includes("book") || q.includes("ticket") || q.includes("slot")) {
    return "To book a ticket, go to the 'Book Darshan Ticket' section, choose your temple, visit purpose, slot, and fill pilgrim details. After confirmation, you will get a QR ticket code.";
  }

  if (q.includes("crowd") || q.includes("rush") || q.includes("waiting")) {
    return "Check the 'Live Crowd Status' card before booking. Low crowd means good time to visit. High or critical crowd means choose a later slot or tomorrow slot.";
  }

  if (q.includes("tomorrow")) {
    return "Tomorrow slots are shown in the 'Tomorrow Available Slots' section. Choose the slot with more availability and lower expected rush.";
  }

  if (q.includes("senior") || q.includes("disabled") || q.includes("assistance")) {
    return "For senior citizens or differently-abled pilgrims, select SeniorSathi assistance during booking. The system will mark your QR ticket for SeniorSathi priority gate support.";
  }

  if (q.includes("offline") || q.includes("internet") || q.includes("kiosk")) {
    return "Pilgrims without internet can use the temple kiosk/helpdesk. Kiosk staff can create an offline QR ticket, which still works with the scanner gate.";
  }

  if (q.includes("aarti")) {
    return "For Aarti viewing, select 'Aarti Viewing' as your visit purpose. The system treats Aarti visitors differently because they usually stay longer than regular darshan visitors.";
  }

  if (q.includes("contact") || q.includes("help") || q.includes("authority")) {
    return "Go to the 'Contact Temple Authorities' section below. You can find emergency helpline, SeniorSathi helpdesk, and temple control room information.";
  }

  return "I can help with ticket booking, live crowd status, tomorrow slots, SeniorSathi assistance, offline kiosk booking, Aarti visits, and temple contact details.";
}

export default function PilgrimAssistantBot() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "bot",
      text: "Namaste! I am Digii AI Sathi. Ask me about booking, crowd rush, tomorrow slots, SeniorSathi, Aarti, or offline kiosk help.",
    },
  ]);

  const [input, setInput] = useState("");

  function sendMessage(event: FormEvent) {
    event.preventDefault();

    const text = input.trim();

    if (!text) return;

    const reply = answerQuestion(text);

    setMessages((prev) => [
      ...prev,
      { role: "user", text },
      { role: "bot", text: reply },
    ]);

    setInput("");
  }

  return (
    <div className="card overflow-hidden">
      <div className="bg-gradient-to-r from-orange-700 to-amber-500 p-5 text-white">
        <p className="text-xs font-black uppercase tracking-widest">
          AI Assistance
        </p>
        <h2 className="mt-1 text-2xl font-black">Digii AI Sathi</h2>
        <p className="mt-1 text-sm text-orange-100">
          Pilgrim guidance for booking, rush, SeniorSathi, and temple help.
        </p>
      </div>

      <div className="max-h-80 space-y-3 overflow-y-auto p-5">
        {messages.map((message, index) => (
          <div
            key={`${message.role}-${index}`}
            className={
              message.role === "bot"
                ? "mr-8 rounded-3xl bg-orange-50 p-4 text-sm font-semibold text-orange-900"
                : "ml-8 rounded-3xl bg-gray-900 p-4 text-sm font-semibold text-white"
            }
          >
            {message.text}
          </div>
        ))}
      </div>

      <form onSubmit={sendMessage} className="border-t border-orange-100 p-4">
        <div className="flex gap-2">
          <input
            className="input"
            value={input}
            onChange={(event) => setInput(event.target.value)}
            placeholder="Ask: When should I visit? How to book?"
          />

          <button className="btn-primary whitespace-nowrap" type="submit">
            Ask
          </button>
        </div>

        <p className="mt-2 text-xs text-gray-500">
          Demo AI assistant. Later we can connect it with Gemini/OpenAI for real
          dynamic answers.
        </p>
      </form>
    </div>
  );
}
