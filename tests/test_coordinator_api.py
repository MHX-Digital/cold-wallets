import tempfile,unittest,uuid
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from broadcaster.store import BroadcastStore
from coordinator.api import ApiError,WatchOnlyApi
from coordinator.disposable_store import DisposableStore
from coordinator.proposal_store import ProposalStore
from coordinator.service import CoordinatorService

class CoordinatorApiTests(unittest.TestCase):
    def setUp(self): self.temp=tempfile.TemporaryDirectory(prefix=f"cold-wallets-test-{uuid.uuid4().hex}-"); self.root=Path(self.temp.name)
    def tearDown(self): self.temp.cleanup()
    def api(self): return WatchOnlyApi(CoordinatorService(ProposalStore(self.root/"proposals.sqlite"),DisposableStore(self.root/"addresses.sqlite")),BroadcastStore(self.root/"broadcast.sqlite"))
    def ethereum(self): return {"from":"0x"+"11"*20,"to":"0x"+"22"*20,"valueWei":"3","nonce":"0","gasLimit":"21000","maxFeePerGasWei":"100","maxPriorityFeePerGasWei":"2","data":"0x","sources":[],"confirmNetwork":"ethereum-mainnet"}
    def test_idempotency_survives_api_restart_and_rejects_mutation(self):
        first=self.api().create_ethereum(self.ethereum(),"persistent-request-key")
        second=self.api().create_ethereum(self.ethereum(),"persistent-request-key")
        self.assertEqual(first,second)
        changed=self.ethereum(); changed["valueWei"]="4"
        with self.assertRaises(ApiError): self.api().create_ethereum(changed,"persistent-request-key")
    def test_bitcoin_review_is_watch_only_and_reports_backend(self):
        payload={"psbtBase64":"cHNidP8A","destination":"bc1qsynthetic","maxFeeSats":"1000","maxFeeRateSatVb":"10","confirmNetwork":"bitcoin-mainnet"}
        summary={"proposalId":"a"*64,"network":"bitcoin-mainnet","inputs":1,"outputs":[{"address":"bc1qsynthetic","value":1}],"fee":1,"estimatedVsize":100,"feeRate":1.0}
        diagnostic=SimpleNamespace(status=SimpleNamespace(value="DETECTED_UNAPPROVED"),backend_type="native",signing_enabled=False)
        with patch("coordinator.api.inspect_psbt",return_value=(object(),summary)),patch("coordinator.api.diagnose",return_value=diagnostic): result=self.api().review_bitcoin(payload,"bitcoin-review-key")
        self.assertFalse(result["signingEnabled"]); self.assertEqual(result["backend"],"DETECTED_UNAPPROVED")
        self.assertFalse(hasattr(self.api(),"sign"))
    def test_client_cannot_set_internal_fields(self):
        for extra in ({"state":"CONFIRMED"},{"transactionHash":"0xdead"},{"maxTotalCost":"1"}):
            payload=self.ethereum()|extra
            with self.assertRaises(ApiError): self.api().create_ethereum(payload,"another-request-key")

if __name__=="__main__": unittest.main()
