from fbchat_muqit import Message

async def ai_chats(self, author_id, user_message, thread_id, thread_type, message_object, model):
    """Processes AI-related messages that start with '.' """

    query = user_message[1:].strip()  # Remove the "." and clean the query

    if not query:
        await message_object.reply("👀")
        await self.send(Message(text="Please provide your chat after . example (. chat here)"), thread_id=thread_id, thread_type=thread_type)
        return

    print(f"{author_id} asked AI: {query}")

    # Initialize chat history for this user in the thread if not already set
    self.chat_history.setdefault(thread_id, {}).setdefault(author_id, [])

    # Store only messages that start with "."
    self.chat_history[thread_id][author_id].append(f"User: {query}")

    # Limit history length per user (adjustable)
    max_history_length = 20
    history_to_pass = "\n".join(self.chat_history[thread_id][author_id][-max_history_length:])

    # Generate AI response using stored history
    full_input = history_to_pass + "\n" + f"User: {query}\nAI:"
    response = model.generate_content(full_input)

    if response.candidates:
        ai_reply = f"@Ter Mux replied\n: {response.text}"
    else:
        ai_reply = "I couldn't process that."

    print(ai_reply)

    # Store AI response in history for this user
    self.chat_history[thread_id][author_id].append(f"AI: {ai_reply}")

    # Send AI-generated reply
    await message_object.reply("👀")
    await self.send(Message(text=ai_reply), thread_id=thread_id, thread_type=thread_type)
