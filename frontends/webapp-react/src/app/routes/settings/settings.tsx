import { view } from "@risingstack/react-easy-state";
import React, { useEffect, useState } from "react";
import { useHistory } from "react-router-dom";
import state from "src/app/states";
import Avatar from "@material-ui/core/Avatar";
import Box from "@material-ui/core/Box";
import Button from "@material-ui/core/Button";
import Divider from "@material-ui/core/Divider";
import Drawer from "@material-ui/core/Drawer";
import Grid from "@material-ui/core/Grid";
import List from "@material-ui/core/List";
import ListItem from "@material-ui/core/ListItem";
import ListItemIcon from "@material-ui/core/ListItemIcon";
import ListItemText from "@material-ui/core/ListItemText";
import TextField from "@material-ui/core/TextField";
import Typography from "@material-ui/core/Typography";
import AccountBoxIcon from "@material-ui/icons/AccountBox";
import SaveIcon from "@material-ui/icons/Save";
import SecurityIcon from "@material-ui/icons/Security";
import { apiEffect, ApiError } from "src/utils";
import "./settings.scss";

export type User = {
  id: string;
  username: string;
  description?: string;
  image?: string;
};

const SettingsPage = (props: { className?: string }) => {
  const [user, setUser] = React.useState<User>();
  const [didMount, setDidMount] = useState(false);
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [newPasswordRepeat, setNewPasswordRepeat] = useState("");
  const [usernameHasError, setUsernameHasError] = useState(false);
  const [usernameErrorMessage, setUsernameErrorMessage] = useState("");
  const [newPasswordHasError, setNewPasswordHasError] = useState(false);
  const [newPasswordErrorMessage, setNewPasswordErrorMessage] = useState("");
  const [newPasswordRepeatHasError, setNewPasswordRepeatHasError] = useState(
    false
  );
  const [
    newPasswordRepeatErrorMessage,
    setNewPasswordRepeatErrorMessage,
  ] = useState("");
  const [receivedResponse, setReceivedResponse] = useState(false);
  const [hasResponseError, setHasResponseError] = useState(false);
  const [responseErrorMessage, setResponseErrorMessage] = useState("");

  // Form submit handler
  const submitUpdate = async (event: React.MouseEvent<HTMLButtonElement>) => {
    event.preventDefault();
    event.stopPropagation();
    event.nativeEvent.stopImmediatePropagation();
    console.log(usernameHasError);
    console.log(newPasswordHasError);
    console.log(newPasswordRepeatHasError);
    setUsernameHasError(false);
    setNewPasswordHasError(false);
    setNewPasswordRepeatHasError(false);
    setReceivedResponse(false);
    setHasResponseError(false);
    setResponseErrorMessage("");
    // Validate fields
    try {
      if (user && username !== user.username) {
        if (username.trim().length <= 0) {
          setUsernameHasError(true);
          setUsernameErrorMessage("Username should not be empty");
          throw new ApiError();
        }
        if (username.trim().length < 3) {
          setUsernameHasError(true);
          setUsernameErrorMessage("Username should have at least 3 characters");
          throw new ApiError();
        }
        if (username.trim().length > 16) {
          setUsernameHasError(true);
          setUsernameErrorMessage(
            "Username should not have more than 16 characters"
          );
          throw new ApiError();
        }
        if (username.trim().match(/[^a-z0-9_]/i) !== null) {
          setUsernameHasError(true);
          setUsernameErrorMessage(
            "Username can only have A-Z, a-z, underscores and 0-9"
          );
          throw new ApiError();
        }
      }

      if (password) {
        if (newPassword.toString().length <= 0) {
          setNewPasswordHasError(true);
          setNewPasswordErrorMessage("Password should not be empty");
          throw new ApiError();
        }
        if (newPassword.toString().length < 6) {
          setNewPasswordHasError(true);
          setNewPasswordErrorMessage(
            "Password should have at least 6 characters"
          );
          throw new ApiError();
        }
        if (newPassword.toString().length >= 21) {
          setNewPasswordHasError(true);
          setNewPasswordErrorMessage(
            "Password should be less than 21 characters"
          );
          throw new ApiError();
        }
      }

      if (newPassword && newPasswordRepeat !== newPassword) {
        setNewPasswordRepeatHasError(true);
        setNewPasswordRepeatErrorMessage("Passwords don't match");
        throw new ApiError();
      }

      // Only submit form if no errors
      if (
        !usernameHasError &&
        !newPasswordHasError &&
        !newPasswordRepeatHasError
      ) {
        await apiEffect(
          {
            path: "/user",
            method: "PUT",
            body: {
              username: username || "",
              current_password: password || "",
              new_password: newPassword || "",
            },
          },
          (response) => {
            setReceivedResponse(true);
          },
          (error) => {
            setReceivedResponse(true);
            setHasResponseError(true);
            setResponseErrorMessage(error.message);
          }
        )();
      }
    } catch (error) {
      // ignore ApiErrors - handled using form helpertext
    }
  };

  let history = useHistory();

  useEffect(() => {
    apiEffect(
      {
        path: "/user",
        method: "GET",
      },
      (response) => {
        setUser(response.data as User);
        setUsername(response.data.username);
        setDidMount(true);
      },
      (error) => {
        setDidMount(true);
        console.warn(error);
      },
      () => state.loggedIn
    )();
  }, []);

  if (!user) {
    if (didMount) {
      return (
        <div>
          <Typography variant="h4">
            You must be logged in to view this page.
          </Typography>
        </div>
      );
    } else {
      return null;
    }
  }

  return (
    <div>
      <Drawer
        className="SettingsPage__drawer"
        variant="permanent"
        classes={{
          paper: "SettingsPage__drawerPaper",
        }}
        anchor="left"
      >
        <Grid
          container
          className="SettingsPage__user"
          alignItems="center"
          justify="center"
          direction="column"
        >
          <Grid item>
            <Typography variant="h4">{user.username}</Typography>
          </Grid>
          <Grid item>
            <Avatar
              className="SettingsPage__avatar"
              src={user.image}
              alt={user.username}
            />
          </Grid>
        </Grid>
        <Divider />
        <List>
          <ListItem
            button
            key="Your Profile"
            onClick={() => history.push("/user/" + user.username)}
          >
            <ListItemIcon>
              <AccountBoxIcon />
            </ListItemIcon>
            <ListItemText primary="Your Profile" />
          </ListItem>
          <ListItem
            button
            key="Security"
            onClick={() => history.push("/settings/")}
          >
            <ListItemIcon>
              <SecurityIcon />
            </ListItemIcon>
            <ListItemText primary="Security" />
          </ListItem>
        </List>
        <Divider />
      </Drawer>
      <main className="SettingsPage__main">
        <Typography className="SettingsPage__heading" variant="h4">
          Security
        </Typography>
        <form className="SettingsPage__form" method="PUT">
          <Grid container direction="column">
            <Grid item>
              <Typography className="SettingsPage__form__header" variant="h5">
                Change Username:
              </Typography>
              <TextField
                className="SettingsPage__form__box"
                variant="outlined"
                margin="dense"
                error={usernameHasError}
                helperText={usernameHasError ? usernameErrorMessage : ""}
                value={username}
                onChange={(event) => setUsername(event.target.value)}
              />
            </Grid>
            <Grid item>
              <Typography className="SettingsPage__form__header" variant="h5">
                Change Password:
              </Typography>
              <TextField
                className="SettingsPage__form__box"
                variant="outlined"
                label="Current password"
                type="password"
                margin="dense"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
              />
              <TextField
                className="SettingsPage__form__box"
                variant="outlined"
                label="New password"
                type="password"
                margin="dense"
                error={newPasswordHasError}
                helperText={newPasswordHasError ? newPasswordErrorMessage : ""}
                value={newPassword}
                onChange={(event) => setNewPassword(event.target.value)}
              />
              <TextField
                className="SettingsPage__form__box"
                variant="outlined"
                label="Confirm new password"
                type="password"
                margin="dense"
                error={newPasswordRepeatHasError}
                helperText={
                  newPasswordRepeatHasError ? newPasswordRepeatErrorMessage : ""
                }
                value={newPasswordRepeat}
                onChange={(event) => setNewPasswordRepeat(event.target.value)}
              />
            </Grid>
          </Grid>
          {receivedResponse ? (
            hasResponseError ? (
              <Typography>{responseErrorMessage}</Typography>
            ) : (
              <Typography>Successfully updated details</Typography>
            )
          ) : (
            ""
          )}
          <Box display="flex" alignItems="end">
            <Button
              variant="contained"
              color="primary"
              size="large"
              className="SettingsPage__form__button"
              startIcon={<SaveIcon />}
              onClick={submitUpdate}
            >
              Save Changes
            </Button>
          </Box>
        </form>
      </main>
    </div>
  );
};

export default view(SettingsPage);
