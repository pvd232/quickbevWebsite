import React from "react";
import ListItem from "@material-ui/core/ListItem";
import ListItemIcon from "@material-ui/core/ListItemIcon";
import ListItemText from "@material-ui/core/ListItemText";
// import ListSubheader from "@material-ui/core/ListSubheader";
import DashboardIcon from "@material-ui/icons/Dashboard";
import ShoppingCartIcon from "@material-ui/icons/ShoppingCart";
import PeopleIcon from "@material-ui/icons/People";
import PinDropIcon from "@material-ui/icons/PinDrop";
import RestaurantMenuIcon from "@material-ui/icons/RestaurantMenu";
// import AssignmentIcon from "@material-ui/icons/Assignment";

const MainListItems = (props) => {
  return (
    <>
      <ListItem
        button
        onClick={() => {
          props.handleDashboardButtonClick(0);
        }}
      >
        <ListItemIcon>
          <DashboardIcon />
        </ListItemIcon>
        <ListItemText primary="Dashboard" />
      </ListItem>
      <ListItem
        button
        onClick={() => {
          props.handleDashboardButtonClick(1);
        }}
      >
        <ListItemIcon>
          <PeopleIcon />
        </ListItemIcon>
        <ListItemText primary="Customers" />
      </ListItem>
      <ListItem
        button
        onClick={() => {
          props.handleDashboardButtonClick(2);
        }}
      >
        <ListItemIcon>
          <ShoppingCartIcon />
        </ListItemIcon>
        <ListItemText primary="Orders" />
      </ListItem>
      <ListItem
        button
        onClick={() => {
          props.handleDashboardButtonClick(3);
        }}
      >
        <ListItemIcon>
          <RestaurantMenuIcon />
        </ListItemIcon>
        <ListItemText primary="Menu" />
      </ListItem>
      <ListItem
        button
        onClick={() => {
          props.handleDashboardButtonClick(4);
        }}
      >
        <ListItemIcon>
          <PinDropIcon />
        </ListItemIcon>
        <ListItemText primary="Businesses" />
      </ListItem>
    </>
  );
};
export default MainListItems;
// export const secondaryListItems = (
//   <div>
//     <ListSubheader inset>Saved reports</ListSubheader>
//     <ListItem button>
//       <ListItemIcon>
//         <AssignmentIcon />
//       </ListItemIcon>
//       <ListItemText primary="Current month" />
//     </ListItem>
//     <ListItem button>
//       <ListItemIcon>
//         <AssignmentIcon />
//       </ListItemIcon>
//       <ListItemText primary="Last quarter" />
//     </ListItem>
//     <ListItem button>
//       <ListItemIcon>
//         <AssignmentIcon />
//       </ListItemIcon>
//       <ListItemText primary="Year-end sale" />
//     </ListItem>
//   </div>
// );
