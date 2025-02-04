from fbchat_muqit import Message, MessageReaction

async def filter_spams(self, mid, author_id, user_message, thread_id, thread_type, current_time):
    """Tracks and handles spam messages."""
    
    if user_message == self.spam_history.get(author_id, {}).get(thread_id, ''):
        self.spam_counts[author_id] = self.spam_counts.get(author_id, 0) + 1
    else:
        self.spam_counts[author_id] = 1  # Reset if a new message is sent
        self.spam_history.setdefault(author_id, {})[thread_id] = user_message

    # Check if the user has sent the same message 5 times
    if self.spam_counts[author_id] >= 5:
        last_spam_time = self.spam_cooldown.get(author_id, 0)
        if current_time - last_spam_time > 30:
            self.spam_cooldown[author_id] = current_time  # Reset spam cooldown
            alert = "⚠️ Ayaw ug paurok anang emong chat mura kag abnormal animala ka!"
            print(alert)
            await self.send(Message(text=alert), thread_id=thread_id, thread_type=thread_type)
            self.spam_counts[author_id] = 0  # Reset the spam count after warning
            await self.reactToMessage(mid, MessageReaction.ANGRY)
        
        return True  # Indicates that spam was detected

    return False  # No spam detected
