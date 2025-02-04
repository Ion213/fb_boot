from fbchat_muqit import Message, MessageReaction

async def filter_messages(self, mid, author_id, user_message, thread_id, thread_type, current_time):
    """Checks for blocked words and warns the user if needed."""
    
    if any(blocked_word in user_message for blocked_word in self.blocked_words):
        last_warning = self.warning_cooldown.get(author_id, 0)

        # Allow the user to send messages after cooldown
        if current_time - last_warning > 30:
            self.chat_history.setdefault(thread_id, {}).setdefault(author_id, []).clear()  # Clear history
            self.warning_cooldown[author_id] = current_time  # Reset cooldown

        # Ignore repeated blocked messages unless the cooldown expires
        if self.chat_history.get(thread_id, {}).get(author_id, []) and "BLOCKED" in self.chat_history[thread_id][author_id][-1]:
            return True  # Ignore if user spams blocked words in a row

        self.warning_cooldown[author_id] = current_time
        self.chat_history.setdefault(thread_id, {}).setdefault(author_id, []).append("BLOCKED")
        alert = "Ayaw pag send ug words nga di allowed diri nga GC!"
        print(alert)
        await self.send(Message(text=alert), thread_id=thread_id, thread_type=thread_type)
        await self.reactToMessage(mid, MessageReaction.ANGRY)
        
        return True  # Indicates that a blocked word was found

    return False  # No blocked words found
