export const notificationService = {
  fetchNotifications: () => {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve([
          {
            id: 'n1',
            title: 'Complaint status update',
            message: 'Your complaint regarding Pothole on Main Street has been updated to Resolved.',
            read: false,
            createdAt: '2026-07-07T09:15:00Z',
          },
          {
            id: 'n2',
            title: 'New Announcement',
            message: 'Water service will be interrupted in Zone 3 tomorrow from 9 AM to 1 PM.',
            read: true,
            createdAt: '2026-07-05T14:00:00Z',
          },
        ]);
      }, 1000);
    });
  },
};

export default notificationService;
