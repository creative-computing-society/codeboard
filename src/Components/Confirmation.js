import React from 'react';
import PropTypes from 'prop-types';
import * as AlertDialog from '@radix-ui/react-alert-dialog';
import './Confirmation.css';

const Confirmation = ({ response, username, onConfirm, onCancel }) => {
  let message = '';
  let avatar = null;

  if (response.ranking !== undefined) {
    message = "Is this really your account?";
    avatar = response.userAvatar ? (
      <img src={response.userAvatar} alt={response.realName} className="avatar" />
    ) : null;
  } else if (response.message) {
    message = response.message;
  } else if (response.error) {
    message = `Verification failed: ${response.error}`;
  }

  return (
    <AlertDialog.Root defaultOpen>
      <AlertDialog.Portal>
        <AlertDialog.Overlay className="AlertDialogOverlay" />
        <AlertDialog.Content className="AlertDialogContent">
          {avatar && <div className="avatar-container">{avatar}</div>}
          <AlertDialog.Title className="AlertDialogTitle">{message}</AlertDialog.Title>
          {response.ranking !== undefined && (
            <AlertDialog.Description className="AlertDialogDescription">
              <p>LeetCodeRank: {response.ranking}</p>
              <p>Username Entered: {username}</p>
            </AlertDialog.Description>
          )}
          <div className="button-container">
            <AlertDialog.Cancel asChild>
              <button className="Button mauve" onClick={onCancel}>Cancel</button>
            </AlertDialog.Cancel>
            <AlertDialog.Action asChild>
              <button className="Button violet" onClick={onConfirm} autoFocus>OK</button>
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