/* Public Firebase web configuration, NOT service-account credentials. */
window.NV_CONFIG = {
  firebase: { apiKey: "", authDomain: "", projectId: "", storageBucket: "", messagingSenderId: "", appId: "" },
  // Optional HTTPS media URLs you own/have permission to stream, indexed by catalog id.
  mediaSources: {},
  // Optional separate origin for uploaded games (not another path on the same origin).
  // Upload iframe/, games/ and texas/ there, preserving their paths.
  gameOrigin: "",
  sourceRepository: "" // Set to your PUBLIC repository URL to offer the modified AGPL source.
};
