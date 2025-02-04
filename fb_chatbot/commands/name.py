from fbchat_muqit import Message, ThreadType

async def change_group_name(self, author_id, user_message, thread_id, thread_type):
    """Handles changing the group name, only allowing admins to do so."""

    # Ensure command is used in a group
    if thread_type != ThreadType.GROUP:
        alert = "⚠ This command can only be used in group chats!"
        await self.send(Message(text=alert), thread_id=thread_id, thread_type=thread_type)
        return

    # Fetch group info
    group_info = await self.fetchThreadInfo(thread_id)
    group_info = group_info.get(thread_id, None)

    if not group_info:
        print(f"Error: Group info for thread_id {thread_id} not found.")
        await self.send(Message(text="⚠ Could not retrieve group information."), thread_id=thread_id, thread_type=thread_type)
        return

    # Get admin list
    admins = group_info.admins if group_info.admins else []

    # Check if author is an admin
    if author_id not in admins:
        alert = "⚠ Only group admins can change the group name!"
        await self.send(Message(text=alert), thread_id=thread_id, thread_type=thread_type)
        return

    new_name = user_message.split("/name", 1)[1].strip().upper()  # Extract new group name

    if new_name:
        try:
            # Debugging: print parameters before changing title
            print(f"Attempting to change group title to: '{new_name}' (Thread ID: {thread_id})")
            await self.changeThreadTitle(new_name, thread_id, thread_type)
            print(f"✅ Group name changed to '{new_name}' by User ID: {author_id}")
            await self.send(Message(text=f"✅ Group name changed to '{new_name}' by User ID: {author_id}"), thread_id=thread_id, thread_type=thread_type)
        except Exception as e:
            print(f"Error changing group name: {e}")
            await self.send(Message(text="⚠ Failed to change the group name."), thread_id=thread_id, thread_type=thread_type)
    else:
        await self.send(Message(text="⚠ Please provide a valid group name! Example: /name New Group Name"), thread_id=thread_id, thread_type=thread_type)
