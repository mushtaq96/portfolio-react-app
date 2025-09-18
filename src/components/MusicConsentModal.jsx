// src/components/MusicConsentModal.jsx
import React from 'react';

// This is a controlled component. It receives props to control its visibility and actions.
const MusicConsentModal = ({ isOpen, onAccept, onDecline }) => {
  // If not open, render nothing (important for performance and correct behavior)
  if (!isOpen) {
    return null;
  }

  return (
    // Backdrop: Covers the whole screen, slightly darkened
    // fixed inset-0: Positions it fixed, covering top/left 0 to bottom/right 0
    // z-50: High z-index to appear above other content
    <div className="fixed inset-0 bg-black bg-opacity-70 flex items-center justify-center z-50 p-4">
      {/* Modal Box: The actual prompt window */}
      {/* bg-[#0a192f]: Matches your site's background color */}
      {/* rounded-lg, shadow-lg: Styling for the box */}
      <div className="bg-[#0a192f] p-6 rounded-lg shadow-xl max-w-md w-full border border-red-600">
        <h3 className="text-xl font-bold text-gray-300 mb-2">
          Calming Background Music?
        </h3>
        <p className="text-gray-400 mb-6">
          Would you like to listen to some calming music while you explore my portfolio?
        </p>
        <div className="flex justify-end space-x-3">
          {/* Decline Button */}
          {/* hover:bg-gray-700: Subtle hover effect */}
          <button
            onClick={onDecline} // Call the function passed from parent
            className="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700 transition-colors"
          >
            No, Thanks
          </button>
          {/* Accept Button */}
          {/* bg-red-600: Matches your site's accent color */}
          <button
            onClick={onAccept} // Call the function passed from parent
            className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition-colors"
          >
            Sounds Good
          </button>
        </div>
      </div>
    </div>
  );
};

export default MusicConsentModal;

// --- Interview POV ---
// Q: Why a separate component?
// A: Separation of Concerns (KISS). The modal's structure/styling is isolated. App.js handles logic.
// Q: Why is it a "controlled component"?
// A: It receives `isOpen`, `onAccept`, `onDecline` as props. App.js controls its state and behavior. This makes it reusable and predictable.
// Q: Why `if (!isOpen) return null;`?
// A: Efficiency. If the modal isn't meant to be shown, don't render its DOM elements at all.