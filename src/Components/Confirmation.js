import React from 'react';
import PropTypes from 'prop-types';
import * as AlertDialog from '@radix-ui/react-alert-dialog';

const Confirmation = ({ response, username, onConfirm, onCancel }) => {
  let message1 = '';

  let avatar = null;
  let realName = '';
  if (response.ranking !== undefined) {
    message1 = "Is this your LeetCode account?";
    realName = response.realName;
    avatar = response.userAvatar ? (
      <img src={response.userAvatar} alt={response.realName} className="avatar" />
    ) : null;
  } else if (response.message) {
    message1 = response.message;
  } else if (response.error) {
    message1 = `Verification failed: ${response.error}`;
  }

  return (
    <AlertDialog.Root defaultOpen>
      <AlertDialog.Portal>
        <AlertDialog.Overlay className="AlertDialogOverlay" />
        <AlertDialog.Content className="AlertDialogContent">
          {avatar && <div className="avatar-container">{avatar}</div>}
          <AlertDialog.Title className="AlertDialogTitle">{realName}</AlertDialog.Title>
          {response.ranking !== undefined && (
            <AlertDialog.Description className="AlertDialogDescription">
              <p>LeetCode Rank: {response.ranking}</p>
              <p>Username: {username}</p>
            </AlertDialog.Description>
          )}
          {/* <AlertDialog.Title className="AlertDialogTitle">{message1}</AlertDialog.Title> */}
          <AlertDialog.Title className="AlertDialogTitle">Confirm registration ?</AlertDialog.Title>
          <div className="button-container">
            <AlertDialog.Cancel asChild>
              <button className="Button mauve" onClick={onCancel}>Cancel</button>
            </AlertDialog.Cancel>
            <AlertDialog.Action asChild>
              <button className="Button violet" onClick={onConfirm} autoFocus>Confirm</button>
            </AlertDialog.Action>
          </div>
        </AlertDialog.Content>
      </AlertDialog.Portal>
    </AlertDialog.Root>
  );
};

Confirmation.propTypes = {
  response: PropTypes.shape({
    realName: PropTypes.string,
    ranking: PropTypes.number,
    userAvatar: PropTypes.string,
    message: PropTypes.string,
    error: PropTypes.string
  }).isRequired,
  username: PropTypes.string.isRequired,
  onConfirm: PropTypes.func.isRequired,
  onCancel: PropTypes.func.isRequired,
};

export default Confirmation;