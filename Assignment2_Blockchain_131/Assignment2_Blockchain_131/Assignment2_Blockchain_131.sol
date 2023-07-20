// Ippokratis kotsanis - DWS - 131 - Assignment 2 - Blockchain

// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract Charity {
    // Δομή για να αποθηκεύεται η πληροφορία των δωρεών
    struct Donation {
        address donor;
        uint amount;
    }

    address private creator;

    // Πίνακας με τις διευθύνσεις των φιλανθρωπικών οργανισμών
    address[] private charities;

    // Χαρτογράφηση για να αποθηκεύονται οι συνολικές δωρεές που έλαβε κάθε φιλανθρωπικός οργανισμός
    mapping(address => uint) private totalDonations;

    // Μεταβλητές για να καταγράφεται η μεγαλύτερη δωρεά
    address private highestDonor;
    uint private highestDonation;

    // Μεταβλητή για να καταγράφεται το συνολικό ποσό που συγκεντρώθηκε από όλες τις δωρεές
    uint private totalAmountRaised;

    // Τροποποιητής για περιορισμό της πρόσβασης από τον δημιουργό του συμβολαίου
    modifier onlyCreator() {
        require(msg.sender == creator, "Only the contract creator can call this function");
        _;
    }

    // constructor του συμβολαίου για αρχικοποίηση των φιλανθρωπικών οργανισμών
    constructor(address[] memory _charities) {
        creator = msg.sender;
        charities = _charities;
    }


    // Μέθοδος για διευκόλυνση της μεταφοράς κεφαλαίων στους φιλανθρωπικούς οργανισμούς και την προοριζόμενη διεύθυνση
    function makeDonation(address destination, uint charityIndex) external payable {
        require((charityIndex < charities.length) && (charityIndex >= 0), "Charity index is invalid!");

        uint donationAmount = msg.value;

        // Έλεγχος για το αν ο δωρητής έχει αρκετά κεφάλαια
        require(donationAmount <= address(this).balance, "Insufficient funds");

        // Υπολογισμός του ποσού που πρόκειται να δοθεί στον φιλανθρωπικό οργανισμό
        uint charityDonation = donationAmount / 10;

        // Ανανέωση του συνολικού ποσού που συγκεντρώθηκε
        totalAmountRaised += charityDonation;

        // Ανανέωση των συνολικών δωρεών του συγκεκριμένου φιλανθρωπικού οργανισμού
        totalDonations[charities[charityIndex]] += charityDonation;

        // Έλεγχος για το αν αυτή η δωρεά είναι η μεγαλύτερη μέχρι στιγμής
        if (charityDonation > highestDonation) {
            highestDonor = msg.sender;
            // Ενημέρωσε το highest donation
            highestDonation = charityDonation;
        }

        // Μεταφορά του ποσού προς τον φιλανθρωπικό οργανισμό
        payable(charities[charityIndex]).transfer(charityDonation);

        // Μεταφορά του υπολοίπου προς τον προορισμό
        payable(destination).transfer(donationAmount - charityDonation);

        // Εκπομπή γεγονότος για τη δωρεά
        emit DonationEvent(msg.sender, donationAmount);
    }



    // Μέθοδος για δωρεά συγκεκριμένου ποσού σε μια φιλανθρωπική οργάνωση με συγκεκριμένο index
    function makeDonation(address destination, uint charityIndex, uint charityDonation) external payable {
        require((charityIndex < charities.length) && (charityIndex >= 0), "Charity index is invalid!"); 
        require(msg.value > 0, "Donation amount should be greater than 0"); 
        require(charityDonation >= (totalAmountRaised / 100), "Donation amount too low"); 
        require(charityDonation <= (totalAmountRaised / 2), "Donation amount too high");

        uint donationAmount = msg.value;

        // Ανανέωση του συνολικού ποσού που συγκεντρώθηκε
        totalAmountRaised += charityDonation;

        // Ανανέωση των συνολικών δωρεών του συγκεκριμένου φιλανθρωπικού οργανισμού
        totalDonations[charities[charityIndex]] += charityDonation;

        // Έλεγχος για το αν αυτή η δωρεά είναι η μεγαλύτερη μέχρι στιγμής
        if (charityDonation > highestDonation) {
            highestDonor = msg.sender;
            // Ενημέρωσε το highest donation
            highestDonation = charityDonation;
        }

        // Μεταφορά του ποσού προς τον φιλανθρωπικό οργανισμό
        payable(charities[charityIndex]).transfer(charityDonation);

        // Μεταφορά του υπολοίπου προς τον προορισμό
        payable(destination).transfer(donationAmount - charityDonation);

        // Εκπομπή γεγονότος για τη δωρεά
        emit DonationEvent(msg.sender, donationAmount);
    }

    // Μέθοδος για την επιστροφή του συνολικού ποσού που συγκεντρώθηκε από όλες τις δωρεές
    function getTotalAmountRaised() public view returns (uint) {
        return totalAmountRaised;
    }

    // Μέθοδος για την επιστροφή του δωρητή με τη μεγαλύτερη δωρεά
    function getHighestDonor() public view onlyCreator returns (address, uint) {
        return (highestDonor, highestDonation);
    }

    // Μέθοδος που επιστρέφει την δωρεά που έλαβε ενας φιλανρθωπικός οργανισμός
    function getCharityAmount(address charityAddress) public view returns (uint) {
        return totalDonations[charityAddress];
    }

    // Μέθοδος για την καταστροφή του συμβολαίου
    function destroy() public onlyCreator {
        selfdestruct(payable(creator));
    }

    // Συμβάν για τη δωρεά
    event DonationEvent(address indexed donor, uint amount);
}