import React, { useState, useEffect, useRef } from "react";
import Form from "react-bootstrap/Form";
let autoComplete;

function handleScriptLoad(updateQuery, autoCompleteRef, props) {
  autoComplete = new window.google.maps.places.Autocomplete(
    autoCompleteRef.current,
    { componentRestrictions: { country: "us" } }
  );
  autoComplete.setFields(["address_components", "formatted_address"]);
  autoComplete.addListener("place_changed", () => {
    handlePlaceSelect(updateQuery, props);
  });
}

async function handlePlaceSelect(updateQuery, props) {
  const addressObject = autoComplete.getPlace();
  const query = addressObject.formatted_address;
  updateQuery(query);
  props.onUpdate(query);
  console.log(addressObject);
}

function SearchLocationInput(props) {
  const [query, setQuery] = useState("");
  const autoCompleteRef = useRef(null);
  useEffect(() => {
    handleScriptLoad(setQuery, autoCompleteRef, props);
  }, [props]);

  return (
    <Form.Control
      type="search"
      name="address"
      ref={autoCompleteRef}
      onChange={(event) => {
        setQuery(event.target.value);
      }}
      placeholder="1234 Main St"
      required
      value={query}
      autocomplete="off"
      style={{ marginBottom: "2%" }}
    />
  );
}

export default SearchLocationInput;
