import React, { useState, useRef, useEffect } from "react";
import clsx from "clsx";
import { makeStyles } from "@material-ui/core/styles";
import CssBaseline from "@material-ui/core/CssBaseline";
import Drawer from "@material-ui/core/Drawer";
import Box from "@material-ui/core/Box";
import AppBar from "@material-ui/core/AppBar";
import Toolbar from "@material-ui/core/Toolbar";
import List from "@material-ui/core/List";
import Typography from "@material-ui/core/Typography";
import Divider from "@material-ui/core/Divider";
import IconButton from "@material-ui/core/IconButton";
import SmokeFreeIcon from "@material-ui/icons/SmokeFree";
import BusinessIcon from "@material-ui/icons/Business";
import LocalDrinkIcon from "@material-ui/icons/LocalDrink";

import HelpIcon from "@material-ui/icons/Help";
import SettingsIcon from "@material-ui/icons/Settings";
import Container from "@material-ui/core/Container";
import Grid from "@material-ui/core/Grid";
import { Link } from "react-router-dom";

import MenuIcon from "@material-ui/icons/Menu";
import ChevronLeftIcon from "@material-ui/icons/ChevronLeft";

import MainListItems from "./listItems";
import Customers from "./Customers";
import Orders from "./Orders";
import Businesses from "./Businesses";
import MerchantEmployees from "./MerchantEmployees";
import Bouncers from "./Bouncers";
import Menu from "./Menu";

import HomeSplash from "./HomeSplash";
import Modal from "@material-ui/core/Modal";
import Button from "@material-ui/core/Button";
import MenuItem from "@material-ui/core/MenuItem";
import ClickAwayListener from "@material-ui/core/ClickAwayListener";
import Grow from "@material-ui/core/Grow";
import Paper from "@material-ui/core/Paper";
import Popper from "@material-ui/core/Popper";
import MenuList from "@material-ui/core/MenuList";
import { LocalStorageManager } from "../../Models";
function Copyright() {
  return (
    <Typography variant="body2" color="textSecondary" align="center">
      {"Copyright © "}
      <Link to="#">The Quick Company</Link> {new Date().getFullYear()}
      {"."}
    </Typography>
  );
}

const drawerWidth = 240;
// the theme here is the default material UI theme because it is imported from /core/styles
const useStyles = makeStyles((theme) => ({
  root: {
    display: "flex",
  },
  toolbar: {
    paddingRight: 24, // keep right padding when drawer closed
  },
  toolbarIcon: {
    display: "flex",
    alignItems: "center",
    justifyContent: "flex-end",
    padding: "0 8px",
    ...theme.mixins.toolbar,
  },
  appBar: {
    zIndex: theme.zIndex.drawer + 1,
    transition: theme.transitions.create(["width", "margin"], {
      easing: theme.transitions.easing.sharp,
      duration: theme.transitions.duration.leavingScreen,
    }),
  },
  appBarShift: {
    marginLeft: drawerWidth,
    width: `calc(100% - ${drawerWidth}px)`,
    transition: theme.transitions.create(["width", "margin"], {
      easing: theme.transitions.easing.sharp,
      duration: theme.transitions.duration.enteringScreen,
    }),
  },
  menuButton: {
    marginRight: 36,
  },
  menuButtonHidden: {
    display: "none",
  },
  title: {
    flexGrow: 1,
  },
  drawerPaper: {
    position: "relative",
    whiteSpace: "nowrap",
    width: drawerWidth,
    transition: theme.transitions.create("width", {
      easing: theme.transitions.easing.sharp,
      duration: theme.transitions.duration.enteringScreen,
    }),
  },
  drawerPaperClose: {
    overflowX: "hidden",
    transition: theme.transitions.create("width", {
      easing: theme.transitions.easing.sharp,
      duration: theme.transitions.duration.leavingScreen,
    }),
    width: theme.spacing(7),
    [theme.breakpoints.up("sm")]: {
      width: theme.spacing(9),
    },
  },
  appBarSpacer: theme.mixins.toolbar,
  content: {
    flexGrow: 1,
    height: "100vh",
    overflow: "auto",
  },
  container: {
    paddingTop: theme.spacing(4),
    paddingBottom: theme.spacing(4),
  },
  paper: {
    padding: theme.spacing(2),
    display: "flex",
    overflow: "auto",
    flexDirection: "column",
    height: "115vh",
    maxHeight: "800px",
  },

  modal: {
    position: "absolute",
    left: "50%",
    top: "50%",
    transform: "translateY(-50%) translateX(-50%)",
    width: 400,
    backgroundColor: theme.palette.background.paper,
    border: "2px solid #000",
    boxShadow: theme.shadows[5],
    padding: theme.spacing(2, 4, 3),
  },
  fixedHeight: {
    height: "115vh",
    maxHeight: "800px",
  },
}));

const Dashboard = (props) => {
  const classes = useStyles();
  const [open, setOpen] = useState(true);
  const [currentPageIndex, setCurrentPageIndex] = useState(0);
  const fixedHeightPaper = clsx(classes.paper, classes.fixedHeight);
  const handleDashboardButtonClick = (newIndex) => {
    setCurrentPageIndex(newIndex);
  };
  const [modalOpen, setModalOpen] = useState(
    LocalStorageManager.shared.firstLogin === "true" ? true : false
  );

  const [settingsOpen, setSettingsOpen] = useState(false);
  const [helpOpen, setHelpOpen] = useState(false);

  const modalHandleClose = () => {
    LocalStorageManager.shared.setItem("first_login", false);
    setModalOpen(false);
  };
  const settingsAnchorRef = useRef(null);
  const helpAnchorRef = useRef(null);

  const handleSettingsToggle = () => {
    setSettingsOpen((prevSettingsOpen) => !prevSettingsOpen);
  };
  const handleHelpToggle = () => {
    setHelpOpen((prevHelpOpen) => !prevHelpOpen);
  };
  const handleSettingsClose = (event) => {
    if (
      settingsAnchorRef.current &&
      settingsAnchorRef.current.contains(event.target)
    ) {
      return;
    }
    setSettingsOpen(false);
  };
  const handleHelpClose = (event) => {
    if (helpAnchorRef.current && helpAnchorRef.current.contains(event.target)) {
      return;
    }
    setHelpOpen(false);
  };
  const prevSettingsOpen = useRef(settingsOpen);
  const prevHelpOpen = useRef(settingsOpen);

  // const handleAddMerchantEmployee = () => {
  //   props.handleAddMerchantEmployee();
  // }
  useEffect(() => {
    if (prevSettingsOpen.current === true && settingsOpen === false) {
      settingsAnchorRef.current.focus();
    }
    if (prevHelpOpen.current === true && helpOpen === false) {
      helpAnchorRef.current.focus();
    }
    prevSettingsOpen.current = settingsOpen;
    prevHelpOpen.current = helpOpen;
  }, [settingsOpen, helpOpen]);
  const pages = [
    <HomeSplash
      // orders={props.orders}
      // businesses={props.businesses}
      fixedHeightPaper={fixedHeightPaper}
      classes={classes}
    />,
    <Customers
      customers={props.customers}
      fixedHeightPaper={fixedHeightPaper}
      classes={classes}
    />,
    <MerchantEmployees
      merchantEmployees={props.merchantEmployees}
      fixedHeightPaper={fixedHeightPaper}
      classes={classes}
      onUpdate={(newMerchantEmployee) =>
        props.updateMerchantEmployee(newMerchantEmployee)
      }
    />,
    <Bouncers
      bouncers={props.bouncers}
      fixedHeightPaper={fixedHeightPaper}
      classes={classes}
    />,
    <Orders
      // drinks={props.drinks}
      // orders={props.orders}
      // businesses={props.businesses}
      fixedHeightPaper={fixedHeightPaper}
      classes={classes}
    />,
    <Menu
      // businesses={props.businesses}
      fixedHeightPaper={fixedHeightPaper}
      classes={classes}
    ></Menu>,
    <Businesses
      // businesses={props.businesses}
      fixedHeightPaper={fixedHeightPaper}
      classes={classes}
      onUpdate={(newBusinesses) => props.updateBusinesses(newBusinesses)}
    />,
  ];

  const handleDrawerOpen = () => {
    setOpen(true);
  };
  const handleDrawerClose = () => {
    setOpen(false);
  };

  // i think this creates one CSS class by combining other CSS classes into multple properies within one unifying class
  const modalBody = (
    <div className={classes.modal}>
      <h2 style={{ marginBottom: "10%" }}>Welcome to Quickbev!</h2>
      <p>
        This is your home base for <strong>managing</strong> your:
      </p>
      <ul style={{ marginLeft: "10%" }}>
        <li>businesses</li>
        <li>business menus</li>
        <li>employee profiles</li>
      </ul>
      <p>
        As well as for <strong>analyzing </strong>and <strong>exporting</strong>{" "}
        your:
      </p>

      <ul style={{ marginLeft: "10%" }}>
        <li>sales data</li>
        <li>order data</li>
        <li>customer data</li>
      </ul>
      <p>
        You can access all these features by clicking the tabs on the left hand
        side of the screen. If you have any questions or need any help, just
        click the question mark button at the top right corner of the screen to
        get in touch with our tech support!
      </p>
      <Button
        style={{
          textAlign: "center",
          marginLeft: "47%",
          transform: "translateX(-47%)",
        }}
        onClick={modalHandleClose}
      >
        Lets get started
      </Button>
    </div>
  );
  return (
    <div className={classes.root}>
      <CssBaseline />
      <AppBar
        position="absolute"
        className={clsx(classes.appBar, open && classes.appBarShift)}
      >
        <Toolbar className={classes.toolbar}>
          <IconButton
            edge="start"
            color="inherit"
            aria-label="open drawer"
            onClick={handleDrawerOpen}
            className={clsx(
              classes.menuButton,
              open && classes.menuButtonHidden
            )}
          >
            <MenuIcon />
          </IconButton>
          <Typography
            component="h1"
            variant="h6"
            color="inherit"
            noWrap
            className={classes.title}
          >
            Dashboard
          </Typography>
          {LocalStorageManager.shared.currentMerchant.isAdministrator ===
          true ? (
            <>
              <IconButton color="inherit" href="/menubuilder">
                <SmokeFreeIcon></SmokeFreeIcon>
              </IconButton>

              <IconButton color="inherit" href="/deactivate-business">
                <LocalDrinkIcon></LocalDrinkIcon>
              </IconButton>

              <IconButton color="inherit" href="/deactivate-drink">
                <BusinessIcon></BusinessIcon>
              </IconButton>
            </>
          ) : null}
          <IconButton
            color="inherit"
            onClick={handleSettingsToggle}
            ref={settingsAnchorRef}
            aria-controls={settingsOpen ? "menu-list-grow" : undefined}
            aria-haspopup="true"
          >
            <SettingsIcon></SettingsIcon>
          </IconButton>
          <Popper
            open={settingsOpen}
            anchorEl={settingsAnchorRef.current}
            role={undefined}
            transition
            disablePortal
          >
            {({ TransitionProps, placement }) => (
              <Grow
                {...TransitionProps}
                style={{
                  transformOrigin:
                    placement === "bottom" ? "center top" : "center bottom",
                }}
              >
                <Paper>
                  <ClickAwayListener onClickAway={handleSettingsClose}>
                    <MenuList autoFocusItem={settingsOpen} id="menu-list-grow">
                      <Link to="/">
                        <MenuItem>Logout</MenuItem>
                      </Link>
                    </MenuList>
                  </ClickAwayListener>
                </Paper>
              </Grow>
            )}
          </Popper>
          <IconButton
            color="inherit"
            onClick={handleHelpToggle}
            ref={helpAnchorRef}
            aria-controls={helpOpen ? "menu-list-grow" : undefined}
            aria-haspopup="true"
          >
            <HelpIcon />
          </IconButton>
          <Popper
            open={helpOpen}
            anchorEl={helpAnchorRef.current}
            role={undefined}
            transition
            disablePortal
          >
            {({ TransitionProps, placement }) => (
              <Grow
                {...TransitionProps}
                style={{
                  transformOrigin:
                    placement === "bottom" ? "center top" : "center bottom",
                }}
              >
                <Paper>
                  <ClickAwayListener onClickAway={handleHelpClose}>
                    <MenuList autoFocusItem={helpOpen} id="menu-list-grow">
                      <MenuItem>Phone: 713-256-5720</MenuItem>
                      <MenuItem>Email: bbucey@utexas.edu</MenuItem>
                    </MenuList>
                  </ClickAwayListener>
                </Paper>
              </Grow>
            )}
          </Popper>
        </Toolbar>
      </AppBar>
      <Drawer
        variant="permanent"
        classes={{
          paper: clsx(classes.drawerPaper, !open && classes.drawerPaperClose),
        }}
        open={open}
      >
        <div className={classes.toolbarIcon}>
          <IconButton onClick={handleDrawerClose}>
            <ChevronLeftIcon />
          </IconButton>
        </div>
        <Divider />
        <List>
          <MainListItems
            handleDashboardButtonClick={(newIndex) => {
              handleDashboardButtonClick(newIndex);
            }}
          />
        </List>
      </Drawer>
      <main className={classes.content}>
        <div className={classes.appBarSpacer} />
        <Container maxWidth="xl" className={classes.container}>
          <Modal
            open={modalOpen}
            aria-labelledby="simple-modal-title"
            aria-describedby="simple-modal-description"
          >
            {modalBody}
          </Modal>
          <Grid container spacing={3}>
            {pages[currentPageIndex]}
          </Grid>
          <Box pt={4}>
            <Copyright />
          </Box>
        </Container>
      </main>
    </div>
  );
};
export default Dashboard;
