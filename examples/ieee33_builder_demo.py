from src.network.benchmarks.ieee33.builder import (
    IEEE33Builder,
)

from src.network.verification.verifier import (
    NetworkVerifier,
)

from src.network.verification.report import (
    VerificationReport,
)


def main() -> None:

    network = IEEE33Builder.build()

    NetworkVerifier.verify(
        network,
    )

    VerificationReport.print(
        network,
    )


if __name__ == "__main__":
    main()
